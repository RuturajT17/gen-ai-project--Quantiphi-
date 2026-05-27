import concurrent.futures
import logging
import os
import time
import warnings

warnings.filterwarnings(
    "ignore",
    message="All support for the `google.generativeai` package has ended.*",
    category=FutureWarning,
)
import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
genai.configure(api_key=GEMINI_API_KEY)
logger = logging.getLogger("genai-employee-analytics.llm")


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


def _classify_error_message(message):
    msg = (message or "").lower()
    if "429" in msg or "rate" in msg or "quota" in msg or "exceeded" in msg:
        return "rate_limit"
    if "timeout" in msg or "timed out" in msg:
        return "timeout"
    if "network" in msg or "connection" in msg or "unavailable" in msg:
        return "network"
    return "generic"


def _friendly_message(error_type):
    if error_type == "rate_limit":
        return "AI request limit reached temporarily. Please wait about 1 minute and try again."
    if error_type == "timeout":
        return "The AI response took too long. Please try again in a moment."
    if error_type == "empty":
        return "Unable to generate insights currently. Please try again."
    return "AI insights are temporarily unavailable. Please try again later."


def _generate(prompt):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(
            model.generate_content,
            prompt,
            generation_config={
                "temperature": 0.6,
            },
        )
        return future.result(timeout=45)


def generate_insight(prompt):
    if not GEMINI_API_KEY:
        return _friendly_message("generic")

    attempt = 0
    while attempt < 2:
        try:
            response = _generate(prompt)
            text = (response.text or "").strip() if response else ""
            if not text:
                logger.warning("[LLM ERROR] type=empty details=empty_response")
                return _friendly_message("empty")
            return text
        except concurrent.futures.TimeoutError:
            logger.warning("[LLM ERROR] type=timeout details=generate_timeout")
            if attempt == 0:
                time.sleep(0.6)
                attempt += 1
                continue
            return _friendly_message("timeout")
        except Exception as exc:
            error_type = _classify_error_message(str(exc))
            logger.warning("[LLM ERROR] type=%s details=%s", error_type, str(exc))
            if error_type in {"network", "timeout"} and attempt == 0:
                time.sleep(0.6)
                attempt += 1
                continue
            return _friendly_message(error_type)
        finally:
            attempt += 1
