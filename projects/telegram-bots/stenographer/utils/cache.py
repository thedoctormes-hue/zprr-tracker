"""Cache utilities for stenographer bot."""
from functools import lru_cache
from pathlib import Path

ALLOWED_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a", ".flac", ".aac", ".opus", ".mp4"}

@lru_cache(maxsize=8)
def load_prompt_cached(prompts_dir: str, filename: str) -> str:
    """Load prompt from file with LRU cache."""
    path = Path(prompts_dir) / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def check_file_size(file_path: str, max_size: int):
    """Check file size against maximum."""
    import os
    from typing import Tuple
    
    try:
        size = os.path.getsize(file_path)
        if size > max_size:
            return False, f"Файл слишком большой: {size / 1024 / 1024:.1f} МБ. Максимум {max_size / 1024 / 1024:.0f} МБ."
        return True, ""
    except FileNotFoundError:
        return False, "Файл не найден"
    except Exception as e:
        return False, f"Ошибка проверки файла: {e}"