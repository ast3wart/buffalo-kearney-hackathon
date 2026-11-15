"""Read a nameplate / component-label photo with Claude vision -> structured fields.

    from xray.extract import read_photo
    read_photo("data/seed/demo/PA/photos/PA-IMG0001.jpg")
    -> {"manufacturer": ..., "part_no": ..., "series": ..., "serial": ..., "date_code": ..., "description": ...,
        "unclear": [...], "confidence": 0.0-1.0, "cached": bool}

Responses are cached by image hash in data/cache/vision/ (committed), so the demo runs offline and without a key;
only a new photo (the live one on stage) calls the API. Model: XRAY_LLM_MODEL (default claude-sonnet-5-5).
"""
import base64
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data/cache/vision"
MODEL = os.environ.get("XRAY_LLM_MODEL", "claude-sonnet-5-5")
MEDIA = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}

PROMPT = """This is a photo of an industrial equipment label (nameplate, data plate or component label).
Transcribe exactly what is printed. Do not guess or correct: if a character is unreadable, put the field name in
"unclear" and give your best partial reading. Copy the catalog/part number character for character, keeping dashes.
Return: manufacturer, part_no (catalog number), series (e.g. "B"), serial, date_code (year on the label, as printed),
description (product line or text under the brand), unclear (fields you could not read with certainty), and
confidence (0-1, how sure you are the part_no is exactly right)."""

SCHEMA = {
    "type": "object",
    "properties": {
        "manufacturer": {"type": "string"},
        "part_no": {"type": "string"},
        "series": {"type": "string"},
        "serial": {"type": "string"},
        "date_code": {"type": "string"},
        "description": {"type": "string"},
        "unclear": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
    "required": ["manufacturer", "part_no", "series", "serial", "date_code", "description", "unclear", "confidence"],
    "additionalProperties": False,
}


def _load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                if v.strip():
                    os.environ.setdefault(k.strip(), v.strip())


def image_hash(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_photo(path, use_api: bool = True) -> dict:
    path = Path(path)
    key = image_hash(path)
    cached = CACHE / f"{key}.json"
    if cached.exists():
        return {**json.loads(cached.read_text()), "cached": True}
    if not use_api:
        raise LookupError(f"no cached reading for {path.name}; run with an API key to read it")

    import anthropic

    _load_env()
    client = anthropic.Anthropic()
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=2000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": MEDIA.get(path.suffix.lower(), "image/jpeg"), "data": data}},
            {"type": "text", "text": PROMPT},
        ]}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"model declined to read {path.name}")
    text = next(b.text for b in response.content if b.type == "text")
    reading = {**json.loads(text), "model": response.model, "image": path.name}
    CACHE.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(reading, indent=2))
    return {**reading, "cached": False}
