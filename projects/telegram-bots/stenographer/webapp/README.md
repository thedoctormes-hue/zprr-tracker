# Stenographer WebApp - Large File Upload

Telegram WebApp for uploading audio/video files up to 2GB with chunked upload.

## Features

- ✅ Drag & Drop upload
- ✅ Chunked upload (10MB chunks)
- ✅ Progress bar
- ✅ Telegram WebApp integration
- ✅ Up to 2GB file support
- ✅ Auto-start processing after upload

## Structure

```
webapp/
├── static/
│   ├── index.html    # Main WebApp interface
│   └── app.js        # JavaScript logic
├── server.py         # FastAPI backend
├── webapp.service    # Systemd service file
├── requirements.txt  # Dependencies
├── INTEGRATION.md    # Bot integration guide
└── README.md         # This file
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Server
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 3. Or with Systemd
```bash
sudo cp webapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now stenographer-webapp
```

## Bot Integration

1. Add `WEBAPP_URL` to `.env`:
```bash
WEBAPP_URL=https://files.stenographerobot.com
```

2. Add `/upload` command handler (already added to `handlers.py`)

3. Users click "Открыть загрузчик" button → WebApp → Upload file → Auto-processing

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/init` | Initialize upload session |
| POST | `/api/upload/chunk` | Upload file chunk |
| POST | `/api/upload/complete` | Complete upload, merge chunks |
| GET | `/api/upload/status/{id}` | Check upload status |

## File Storage

Files stored at: `/var/lib/stenographer/uploads/{upload_id}/`

Each upload contains:
- `{filename}` - The uploaded file (merged chunks)
- `metadata.json` - Upload metadata