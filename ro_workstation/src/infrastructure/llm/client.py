from __future__ import annotations

import json

try:
    import ollama
except Exception:  # pragma: no cover - graceful fallback when Ollama SDK is unavailable.
    ollama = None

from src.core.config.config_loader import get_app_settings


class LLMClient:
    """Thin Ollama client with resilient offline fallbacks."""

    def __init__(self) -> None:
        settings = get_app_settings()
        self.model = settings.ollama_model
        self.client = ollama.Client(host=settings.ollama_host) if ollama else None

    def generate(self, prompt: str, system: str = "") -> str:
        try:
            if not self.client:
                raise RuntimeError("Ollama client unavailable")
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            )
            return response["message"]["content"]
        except Exception:
            return f"[Ollama Offline Mode] Simulated response for: {prompt[:50]}..."

    def generate_json(self, prompt: str, system: str = "") -> dict:
        raw = self.generate(prompt, f"{system}\nRespond ONLY with valid JSON.")
        if "[Ollama Offline Mode]" in raw:
            return {"status": "offline_stub", "prompt": prompt}
        clean = raw.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON from LLM", "raw": raw}
