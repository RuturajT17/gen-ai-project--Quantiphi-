import concurrent.futures
import os

import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
genai.configure(api_key=GEMINI_API_KEY)


def _normalize_model_name(name):
    if not name:
        return ""
    return name.replace("models/", "")


def _resolve_model_name(preferred):
    preferred_norm = _normalize_model_name(preferred)
    try:
        models = list(genai.list_models())
    except Exception:
        return preferred

    candidates = [
        m.name
        for m in models
        if "generateContent" in getattr(m, "supported_generation_methods", [])
    ]
    if preferred in candidates:
        return preferred
    if preferred_norm:
        for name in candidates:
            if _normalize_model_name(name) == preferred_norm:
                return name
        for name in candidates:
            if name.endswith(preferred_norm):
                return name
    for name in candidates:
        if "gemini-1.5-flash" in name:
            return name
    return candidates[0] if candidates else preferred


MODEL_NAME = _resolve_model_name(GEMINI_MODEL)
model = genai.GenerativeModel(MODEL_NAME)


def generate_insight(prompt):
    try:
        if not GEMINI_API_KEY:
            return "Error generating insight: GEMINI_API_KEY is not set."
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.6,
                },
            )
            response = future.result(timeout=45)
        if not response.text:
            return "Unable to generate insights at this time."
        return response.text
    except concurrent.futures.TimeoutError:
        return "Error generating insight: request timed out."
    except Exception as exc:
        return f"Error generating insight: {exc}"
