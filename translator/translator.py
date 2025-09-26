"""Glue code to map parsed orders to the 3Commas API client."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .client import ThreeCommasClient, ThreeCommasConfig
from .parser import OrderInstruction, OrderParser, OrderParserError


@dataclass
class Translator:
    """Translate raw messages into API payloads and send them to 3Commas."""

    client: ThreeCommasClient
    parser: OrderParser

    def translate_and_execute(self, message: str) -> Dict[str, Any]:
        instruction = self.parser.parse(message)
        payload = instruction.as_payload(self.client.config.account_id)
        payload["side"] = instruction.side
        return self.client.create_simple_trade(payload)


__all__ = ["Translator", "OrderParser", "OrderParserError", "OrderInstruction"]
