"""Minimal 3Commas API client."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


LOGGER = logging.getLogger(__name__)


@dataclass
class ThreeCommasConfig:
    """Configuration data for the :class:`ThreeCommasClient`."""

    api_key: str
    api_secret: str
    account_id: int
    base_url: str = "https://api.3commas.io/public/api"
    timeout: int = 30
    dry_run: bool = False


class ThreeCommasClient:
    """Very small subset of the 3Commas API focusing on smart trade creation."""

    def __init__(self, config: ThreeCommasConfig):
        self.config = config

    def create_simple_trade(self, instruction: Dict[str, Any]) -> Dict[str, Any]:
        """Create a smart trade using the `/smart_trades/create_simple_{side}` endpoint.

        Parameters
        ----------
        instruction: dict
            The payload generated from :meth:`translator.parser.OrderInstruction.as_payload`.
        """
        side = instruction.get("side") or self._infer_side_from_position(instruction)
        endpoint = f"/ver1/smart_trades/create_simple_{side}"
        payload = {k: v for k, v in instruction.items() if k != "side"}
        response = self._request("POST", endpoint, payload)
        return response

    def _infer_side_from_position(self, instruction: Dict[str, Any]) -> str:
        side = instruction.get("side")
        if side:
            return side
        position = instruction.get("position", {})
        position_type = position.get("type")
        return "buy" if position_type != "sell" else "sell"

    def _request(self, method: str, endpoint: str, payload: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.config.base_url}{endpoint}"
        payload = payload or {}
        body = json.dumps(payload, separators=(",", ":"))
        signature = self._sign(body)

        headers = {
            "APIKEY": self.config.api_key,
            "Signature": signature,
            "Content-Type": "application/json",
        }

        if self.config.dry_run:
            LOGGER.info("Dry run enabled. Would send %s %s with payload %s", method, url, body)
            return {"status": "dry_run", "method": method, "url": url, "payload": payload}

        response = requests.request(
            method,
            url,
            data=body,
            headers=headers,
            timeout=self.config.timeout,
        )
        response.raise_for_status()
        return response.json()

    def _sign(self, payload: str) -> str:
        secret = self.config.api_secret.encode("utf-8")
        timestamp = str(int(time.time()))
        body = timestamp + payload
        digest = hmac.new(secret, body.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{timestamp}:{digest}"


__all__ = ["ThreeCommasConfig", "ThreeCommasClient"]
