"""
Stenographer WebApp Backend
FastAPI server for chunked file upload (up to 2GB)
"""

import os
import secrets
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging - detailed for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Stenographer WebApp API")

# Resolve paths relative to this file
BASE_DIR = Path(__file__).parent.resolve()
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), html=True, check_dir=False), name="static")

# Configuration
UPLOAD_DIR = Path("/var/lib/stenographer/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_DIR = UPLOAD_DIR / "chunks"
CHUNK_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB

# In-memory upload sessions (use Redis in production)
upload_sessions: Dict[str, dict] = {}


class UploadInitRequest(BaseModel):
    filename: str
    size: int
    type: str
    total_chunks: int


class UploadCompleteRequest(BaseModel):
    upload_id: str


def verify_telegram_init_data(init_data: str) -> bool:
    """Verify Telegram WebApp init data (simplified version)"""
    if not init_data:
        logger.warning("⚠️ Empty init_data received - may fail on iOS")
    return True


def generate_upload_id() -> str:
    """Generate unique upload ID"""
    return secrets.token_urlsafe(32)


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main page"""
    logger.info("📄 Index page requested")
    index_path = STATIC_DIR / "index.html"
    with open(index_path) as f:
        return f.read()


@app.post("/api/upload/init")
async def init_upload(request: UploadInitRequest, request_obj: Request, x_telegram_init_data: Optional[str] = Header(None)):
    client_ip = request_obj.client.host if request_obj.client else "unknown"
    logger.info(f"📥 UPLOAD INIT from {client_ip}")
    logger.info(f"   filename={request.filename}, size={request.size}, type={request.type}")
    logger.info(f"   init_data present: {bool(x_telegram_init_data)}, len={len(x_telegram_init_data or '')}")

    if not verify_telegram_init_data(x_telegram_init_data or ""):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")

    if request.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    upload_id = generate_upload_id()

    # Create upload directory
    upload_path = UPLOAD_DIR / upload_id
    upload_path.mkdir(exist_ok=True)

    # Store session
    upload_sessions[upload_id] = {
        "filename": request.filename,
        "size": request.size,
        "type": request.type,
        "total_chunks": request.total_chunks,
        "uploaded_chunks": 0,
        "created_at": datetime.now().isoformat()
    }

    logger.info(f"✅ Upload session created: {upload_id}")
    return {"upload_id": upload_id, "chunk_size": CHUNK_SIZE}


@app.post("/api/upload/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk_data: UploadFile = File(...),
    x_telegram_init_data: Optional[str] = Header(None),
    request_obj: Request = None
):
    client_ip = request_obj.client.host if request_obj and request_obj.client else "unknown"
    logger.info(f"📤 CHUNK {upload_id}_{chunk_index} from {client_ip}")
    logger.info(f"   content_type={chunk_data.content_type}, filename={chunk_data.filename}")

    if not verify_telegram_init_data(x_telegram_init_data or ""):
        logger.error(f"❌ Auth failed for chunk {upload_id}_{chunk_index}")
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")

    if upload_id not in upload_sessions:
        logger.error(f"❌ Upload session not found: {upload_id}")
        raise HTTPException(status_code=404, detail="Upload session not found")

    # Save chunk
    chunk_path = CHUNK_DIR / f"{upload_id}_chunk_{chunk_index}"
    content = await chunk_data.read()
    logger.info(f"   chunk size={len(content)} bytes")

    with open(chunk_path, "wb") as f:
        f.write(content)

    # Update session
    upload_sessions[upload_id]["uploaded_chunks"] += 1
    logger.info(f"✅ Chunk saved: {chunk_index}/{upload_sessions[upload_id]['total_chunks']}")

    return {"status": "ok", "chunk_index": chunk_index}


@app.post("/api/upload/complete")
async def complete_upload(request: UploadCompleteRequest, x_telegram_init_data: Optional[str] = Header(None)):
    logger.info(f"🏁 COMPLETE upload: {request.upload_id}")

    if not verify_telegram_init_data(x_telegram_init_data or ""):
        raise HTTPException(status_code=401, detail="Invalid Telegram auth")

    if request.upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[request.upload_id]

    # Combine chunks
    upload_path = UPLOAD_DIR / request.upload_id
    output_file = upload_path / session["filename"]

    with open(output_file, "wb") as outfile:
        for i in range(session["total_chunks"]):
            chunk_path = CHUNK_DIR / f"{request.upload_id}_chunk_{i}"
            if chunk_path.exists():
                with open(chunk_path, "rb") as infile:
                    outfile.write(infile.read())
                chunk_path.unlink()

    # Save metadata for bot processing
    metadata_path = upload_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump({
            "upload_id": request.upload_id,
            "filename": session["filename"],
            "size": session["size"],
            "type": session["type"],
            "init_data": x_telegram_init_data or "",
            "completed_at": datetime.now().isoformat()
        }, f, indent=2)

    # Notify bot via webhook (for iOS where sendData doesn't work)
    try:
        import aiohttp
        bot_token = os.getenv("BOT_TOKEN")
        chat_id = os.getenv("WEBAPP_CHAT_ID")
        if bot_token and chat_id:
            async with aiohttp.ClientSession() as session_http:
                await session_http.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": f"📤 WebApp upload complete: {session['filename']}\nData: action=upload_complete&upload_id={request.upload_id}"
                    }
                )
            logger.info(f"✅ Bot notified via webhook")
    except Exception as e:
        logger.error(f"⚠️ Failed to notify bot: {e}")

    logger.info(f"✅ Upload complete: {output_file}")
    return {"status": "complete", "file_path": str(output_file)}


@app.get("/api/upload/status/{upload_id}")
async def get_upload_status(upload_id: str):
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")

    session = upload_sessions[upload_id]
    return {
        "upload_id": upload_id,
        "progress": session["uploaded_chunks"] / session["total_chunks"] * 100,
        "uploaded_chunks": session["uploaded_chunks"],
        "total_chunks": session["total_chunks"]
    }


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)