"""
Shared classifier module — объединённый классификатор для Protocol и ЗПРР Трекер
Pydantic валидация + async ffmpeg для транскрипции
"""
import asyncio
import base64
import json
import logging
import os
from typing import Optional

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Pydantic модели
class SemanticVector(BaseModel):
    task: float = Field(ge=0, le=1)
    idea: float = Field(ge=0, le=1)
    identity: float = Field(ge=0, le=1)
    knowledge: float = Field(ge=0, le=1)
    pattern: float = Field(ge=0, le=1)

class Emotion(BaseModel):
    positive: float = Field(ge=0, le=1)
    negative: float = Field(ge=0, le=1)
    neutral: float = Field(ge=0, le=1)

    def normalize(self):
        total = self.positive + self.negative + self.neutral
        if total > 0:
            self.positive /= total
            self.negative /= total
            self.neutral /= total

class FragmentClassification(BaseModel):
    semantic_vector: SemanticVector = Field(default_factory=SemanticVector)
    emotion: Emotion = Field(default_factory=lambda: Emotion(positive=0, negative=0, neutral=1.0))
    three_interpretations: list[str] = Field(default_factory=lambda: ["—", "—", "—"])
    conflict_detected: bool = False
    unknown_type: bool = False
    people: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    summary: str = "Классификация недоступна"
    confidence: float = Field(ge=0, le=1, default=0.0)
    meta: dict = Field(default_factory=dict)

    def model_post_init(self, __context):
        self.emotion.normalize()

# Промпты
CLASSIFY_PROMPT = """Ты — классификатор фрагментов памяти для системы "Протокол".

Твоя задача: принять текстовый фрагмент и вернуть ТОЛЬКО валидный JSON без markdown, без пояснений, без преамбул.

Схема ответа:
{
  "semantic_vector": {"task": 0.0, "idea": 0.0, "identity": 0.0, "knowledge": 0.0, "pattern": 0.0},
  "emotion": {"positive": 0.0, "negative": 0.0, "neutral": 1.0},
  "three_interpretations": ["через призму роста: ...", "через призму защиты: ...", "через призму связи: ..."],
  "conflict_detected": false,
  "unknown_type": false,
  "people": [],
  "tags": [],
  "summary": "одно предложение — суть фрагмента",
  "confidence": 0.0,
  "meta": {}
}"""

TRANSCRIBE_PROMPT = "Транскрибируй речь точно, без правок"

def _fallback_result(text: str) -> dict:
    """Возвращает заглушку при ошибке моделей."""
    return FragmentClassification(meta={"error": "all_models_failed"}).model_dump()

async def classify_fragment(text: str, primary_model: str, fallback_model: str, api_key: str) -> dict:
    """
    Классифицирует фрагмент через OpenRouter.
    Пробует primary модель, при ошибке — fallback.
    """
    for model in [primary_model, fallback_model]:
        try:
            result = await _call_openrouter(text, model, api_key)
            logger.debug(f"[classifier] success with {model}")
            return result
        except Exception as e:
            logger.warning(f"[classifier] {model} failed: {e}")

    logger.error("[classifier] all models failed, returning fallback")
    return _fallback_result(text)

async def _call_openrouter(text: str, model: str, api_key: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": CLASSIFY_PROMPT},
                    {"role": "user", "content": text},
                ],
                "temperature": 0.3,
                "max_tokens": 800,
            },
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        clean = raw.strip().removeprefix("```json").removesuffix("```").strip()
        data = json.loads(clean)
        return FragmentClassification(**data).model_dump()

async def transcribe_audio(
    file_path: str,
    api_key: str,
    model: str = "google/gemini-2.0-flash-lite-001",
    timeout: int = 60
) -> str:
    """
    Транскрибирует аудиофайл через OpenRouter.
    Использует async ffmpeg для конвертации.
    """
    wav_path = os.path.splitext(file_path)[0] + "_converted.wav"
    try:
        logger.info(f"[transcribe] converting {file_path} -> {wav_path}")
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", file_path, "-ar", "16000", "-ac", "1", "-y", wav_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

        with open(wav_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        logger.info(f"[transcribe] audio encoded, size={len(audio_b64)}")

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": TRANSCRIBE_PROMPT},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Транскрибируй это аудио:"},
                                {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "wav"}},
                            ],
                        },
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)