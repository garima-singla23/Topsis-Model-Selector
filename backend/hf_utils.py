from huggingface_hub import list_models
import random

# Load HF models ONCE at startup
def _load_models():
    models = list_models(
        filter="text-classification",
        limit=200
    )
    return {m.modelId: m for m in models}

HF_MODELS = _load_models()


def fetch_text_classification_models(limit=50):
    """
    Returns a list of text-classification model IDs
    """
    return list(HF_MODELS.keys())[:limit]


# --------- Heuristic Estimators ---------
def estimate_accuracy(model_id):
    model_id = model_id.lower()
    if "large" in model_id:
        return round(random.uniform(0.88, 0.93), 3)
    if "base" in model_id:
        return round(random.uniform(0.82, 0.88), 3)
    return round(random.uniform(0.75, 0.82), 3)


def estimate_latency(model_id):
    model_id = model_id.lower()
    if "large" in model_id:
        return random.randint(120, 200)
    if "base" in model_id:
        return random.randint(60, 120)
    return random.randint(30, 60)


def estimate_model_size(model_id):
    model_id = model_id.lower()
    if "large" in model_id:
        return 600
    if "base" in model_id:
        return 420
    return 250


def estimate_language_coverage(model_id):
    model_id = model_id.lower()
    if "xlm" in model_id or "multi" in model_id:
        return 10
    if "english" in model_id:
        return 2
    return 4


def get_model_metadata(model_ids):
    metadata = {}
    for mid in model_ids:
        metadata[mid] = {
            "accuracy": estimate_accuracy(mid),
            "latency": estimate_latency(mid),
            "size": estimate_model_size(mid),
            "languages": estimate_language_coverage(mid)
        }
    return metadata
