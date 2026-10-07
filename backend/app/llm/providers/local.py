"""
LocalProvider: Implements LLMProvider for local models running via Ollama.

Configuration (via environment variables):
  LLM_PROVIDER=local
  LLM_MODEL=qwen3:4b-instruct                     # Ollama model name
  OLLAMA_BASE_URL=http://localhost:11434          # optional, default http://localhost:11434
"""

import os
import logging
import httpx

from app.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class LocalProvider(LLMProvider):
    """
    Calls a local Ollama server to run LLM inference.
    """

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")

    # ------------------------------------------------------------------
    # Public interface (LLMProvider contract)
    # ------------------------------------------------------------------

    def generate(self, prompt: str) -> str:
        model_id = os.getenv("LLM_MODEL", "").strip()
        if not model_id:
            raise RuntimeError(
                "LocalProvider: LLM_MODEL environment variable is not set. "
                "Set LLM_MODEL to an Ollama model name (e.g. 'qwen3:4b-instruct')."
            )

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0  # deterministic
            }
        }

        try:
            # We use a long timeout since local inference can take time
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "").strip()
        except httpx.RequestError as e:
            raise RuntimeError(f"LocalProvider: Failed to connect to Ollama at {self.base_url}. Is Ollama running? Error: {e}")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"LocalProvider: Ollama API returned error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"LocalProvider: Error generating response from Ollama: {e}")

    def health(self) -> dict:
        model_id = os.getenv("LLM_MODEL", "").strip()
        is_running = False
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self.base_url}/api/tags")
                is_running = r.status_code == 200
        except Exception:
            pass

        return {
            "status": "ok" if is_running else "error",
            "provider": "local",
            "model_configured": bool(model_id),
            "ollama_running": is_running,
            "model": model_id or "not-configured",
        }

    def model_name(self) -> str:
        model_id = os.getenv("LLM_MODEL", "local-mock-model").strip()
        return model_id