"""
JavaBridgeClient - Integration gateway module for communicating with external Java backend.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

try:
    import httpx
except ImportError:
    httpx = None

from schemas.models import KandinskyPromptSchema, PostDraftSchema

# Reconfigure stdout encoding for Windows CP1251 compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logger = logging.getLogger("java_bridge_integration")


class JavaBridgeClient:
    """
    Async HTTP client for dispatching generated content artifacts
    (post drafts, Kandinsky prompts) to external Java backend.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Initializes the client with base URL and timeout setting.

        :param base_url: Base Java backend URL (defaults to env UCUST_JAVA_BACKEND_URL).
        :param timeout: Request timeout in seconds (defaults to env UCUST_JAVA_TIMEOUT).
        """
        raw_url = base_url or os.getenv("UCUST_JAVA_BACKEND_URL", "http://localhost:8080/api/v1")
        self.base_url = raw_url.rstrip("/")

        env_timeout = os.getenv("UCUST_JAVA_TIMEOUT", "10.0")
        try:
            self.timeout = float(timeout if timeout is not None else env_timeout)
        except ValueError:
            self.timeout = 10.0

        logger.info(
            "JavaBridgeClient initialized with base_url='%s', timeout=%.1fs",
            self.base_url,
            self.timeout,
        )

    async def _post_json(self, endpoint: str, payload: Dict[str, Any]) -> bool:
        """
        Internal helper for making async JSON POST requests to Java backend endpoints.

        Handles network timeouts, 5xx server errors, and client errors safely.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if httpx is not None:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, json=payload, headers=headers)
                    if response.is_success:
                        logger.info(
                            "Successfully sent payload to Java backend (%s): HTTP %d",
                            url,
                            response.status_code,
                        )
                        return True
                    else:
                        logger.error(
                            "Java backend returned error (%s): HTTP %d - Response: %s",
                            url,
                            response.status_code,
                            response.text[:200],
                        )
                        return False
            except httpx.TimeoutException as exc:
                logger.error("Timeout sending request to Java backend (%s): %s", url, exc)
                return False
            except httpx.HTTPError as exc:
                logger.error("HTTP error during request to Java backend (%s): %s", url, exc)
                return False
            except Exception as exc:
                logger.error("Unexpected error sending request to Java backend (%s): %s", url, exc)
                return False
        else:
            # Fallback using urllib.request via asyncio.to_thread
            def sync_post() -> bool:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")
                try:
                    with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                        status = resp.getcode()
                        if 200 <= status < 300:
                            logger.info(
                                "Successfully sent payload to Java backend (%s): HTTP %d",
                                url,
                                status,
                            )
                            return True
                        logger.error("Java backend returned error (%s): HTTP %d", url, status)
                        return False
                except urllib.error.HTTPError as exc:
                    logger.error("Java backend returned HTTP error (%s): HTTP %d", url, exc.code)
                    return False
                except urllib.error.URLError as exc:
                    logger.error("Network/Connection error sending request to Java backend (%s): %s", url, exc.reason)
                    return False
                except Exception as exc:
                    logger.error("Unexpected error sending request to Java backend (%s): %s", url, exc)
                    return False

            return await asyncio.to_thread(sync_post)

    async def send_post_draft(self, job_id: int, draft: PostDraftSchema) -> bool:
        """
        Sends generated post draft text and uniqueness metrics to Java backend.

        :param job_id: Unique pipeline task identifier.
        :param draft: PostDraftSchema instance containing post text & score.
        :return: True if successfully accepted by Java server, False otherwise.
        """
        payload = {
            "job_id": job_id,
            "post_text": draft.text,
            "uniqueness_score": draft.uniqueness_score,
            "duplicates_found": draft.duplicates_found,
        }
        logger.info("Sending post draft for job_id=%d to Java backend...", job_id)
        return await self._post_json("post-draft", payload)

    async def send_kandinsky_prompts(
        self,
        job_id: int,
        prompts: List[KandinskyPromptSchema],
    ) -> bool:
        """
        Sends generated Kandinsky image prompts to Java backend.

        :param job_id: Unique pipeline task identifier.
        :param prompts: List of KandinskyPromptSchema instances.
        :return: True if successfully accepted by Java server, False otherwise.
        """
        payload = {
            "job_id": job_id,
            "prompts": [p.model_dump() for p in prompts],
        }
        logger.info("Sending %d Kandinsky prompts for job_id=%d to Java backend...", len(prompts), job_id)
        return await self._post_json("kandinsky-prompts", payload)


# Singleton instance pattern & Dependency Injection provider
_java_bridge_client_instance: Optional[JavaBridgeClient] = None


def get_java_bridge_client() -> JavaBridgeClient:
    """
    Dependency Injection provider & Singleton getter for JavaBridgeClient.
    Can be used directly or as a FastAPI Depends(...) provider.
    """
    global _java_bridge_client_instance
    if _java_bridge_client_instance is None:
        _java_bridge_client_instance = JavaBridgeClient()
    return _java_bridge_client_instance


__all__ = [
    "JavaBridgeClient",
    "get_java_bridge_client",
]
