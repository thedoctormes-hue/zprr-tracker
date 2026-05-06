"""LLM Model Selector — подбор модели под задачу."""
from .selector import (
    select_model, compare_models, MODEL_REGISTRY, TASK_MAPPING,
    fetch_and_store_full_models, analyze_model_family, load_full_models, MODEL_COLUMNS
)

__all__ = [
    "select_model", "compare_models", "MODEL_REGISTRY", "TASK_MAPPING",
    "fetch_and_store_full_models", "analyze_model_family", "load_full_models", "MODEL_COLUMNS"
]