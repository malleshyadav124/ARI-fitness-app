import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from backend.utils.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"

# Supported Groq model (do not depend on config)
DEFAULT_GROQ_MODEL = "llama-3.1-8b-instant"


class GroqClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or GROQ_API_KEY
        # Always use supported model; ignore config/env
        self.model = model if model else DEFAULT_GROQ_MODEL

        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:

        # Validate messages
        if not messages or not isinstance(messages, list):
            raise ValueError("Messages must be a non-empty list")

        for msg in messages:
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"Invalid message format: {msg}")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                GROQ_CHAT_COMPLETIONS_URL,
                headers=headers,
                json=payload,
            )

            # Debug output before any error handling
            print("====== GROQ DEBUG START ======")
            print("Payload being sent to Groq:", json.dumps(payload, indent=2))
            print("Status Code:", resp.status_code)
            print("Response Headers:", dict(resp.headers))
            print("Full Response Text:", resp.text)
            print("====== GROQ DEBUG END ======")

            # Check status code and return error string instead of raising
            if resp.status_code != 200:
                error_msg = f"GROQ ERROR: Status {resp.status_code} - {resp.text}"
                logger.error(error_msg)
                return error_msg

            # Parse JSON response
            try:
                data = resp.json()
            except Exception as e:
                error_msg = f"GROQ ERROR: Failed to parse JSON response - {str(e)}. Response text: {resp.text}"
                logger.error(error_msg)
                return error_msg

            if "choices" not in data or not data.get("choices"):
                error_msg = f"GROQ ERROR: Unexpected response format - no 'choices' field. Response: {json.dumps(data)}"
                logger.error(error_msg)
                return error_msg

            return data["choices"][0]["message"]["content"]


def try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None

    text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except Exception:
            return None

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    candidate = text[start : end + 1]

    try:
        return json.loads(candidate)
    except Exception:
        return None

