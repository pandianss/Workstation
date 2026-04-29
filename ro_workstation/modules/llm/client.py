import os
import json
import ollama

class LLMClient:
    def __init__(self):
        self.model    = os.getenv("OLLAMA_MODEL", "mistral")
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client   = ollama.Client(host=self.base_url)

    def generate(self, prompt: str, system: str = "") -> str:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt}
                ]
            )
            return response["message"]["content"]
        except Exception as e:
            # Fallback for when Ollama is not running in dev environment
            return f"[Ollama Offline Mode] Simulated response for: {prompt[:50]}..."

    def generate_json(self, prompt: str, system: str = "") -> dict:
        """Force JSON output. Strip markdown fences before parsing."""
        raw = self.generate(prompt, system + "\nRespond ONLY with valid JSON.")
        if "[Ollama Offline Mode]" in raw:
            return {"status": "offline_stub", "prompt": prompt}
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean.removeprefix("```json")
        elif clean.startswith("```"):
            clean = clean.removeprefix("```")
        if clean.endswith("```"):
            clean = clean.removesuffix("```")
        clean = clean.strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON from LLM", "raw": raw}
