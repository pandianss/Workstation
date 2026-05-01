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
        """Generate a response and parse it as JSON. Raises RuntimeError or ValueError on failure."""
        augmented_system = (
            f"{system}\n\n"
            "CRITICAL: Respond ONLY with a valid JSON object. "
            "Do not include markdown code fences (```), explanations, "
            "or any text before or after the JSON object. "
            "Start your response with '{' and end with '}'."
        )
        raw = self.generate(prompt, augmented_system)

        if "[Ollama Offline Mode]" in raw:
            raise RuntimeError(
                "LLM is unavailable — Ollama is not reachable. "
                "Check that the Ollama service is running on the configured host."
            )

        clean = raw.strip()
        # Strip markdown fences if the model added them anyway
        for fence in ("```json", "```"):
            clean = clean.replace(fence, "")
        clean = clean.strip()

        # Extract the outermost JSON object if there is surrounding prose
        start = clean.find("{")
        end = clean.rfind("}") + 1
        if start >= 0 and end > start:
            clean = clean[start:end]

        try:
            return json.loads(clean)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM returned invalid JSON: {exc}\n"
                f"Raw output (first 300 chars): {raw[:300]}"
            ) from exc
