"""Parsers turning natural-language order instructions into structured data."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class OrderInstruction:
    """Structured representation of a trading order."""

    side: str
    pair: str
    quantity: float
    order_type: str
    price: Optional[float] = None

    def as_payload(self, account_id: int) -> dict:
        """Return a payload ready to be sent to the 3Commas API."""
        payload = {
            "account_id": account_id,
            "pair": self.pair,
            "position": {
                "type": "market" if self.order_type == "market" else "limit",
                "units": {
                    "value": self.quantity,
                },
            },
        }

        if self.order_type == "limit":
            payload["position"]["price"] = {
                "value": self.price,
            }

        return payload


class OrderParserError(RuntimeError):
    """Raised when the parser cannot extract a well-formed order instruction."""


class OrderParser:
    """Parse natural language instructions into :class:`OrderInstruction` objects."""

    BUY_TOKENS = {
        "buy",
        "achète",
        "achete",
        "achat",
    }
    SELL_TOKENS = {
        "sell",
        "vends",
        "vendre",
        "vend",
        "revends",
        "revendre",
    }
    LIMIT_TOKENS = {"limit", "limite"}
    MARKET_TOKENS = {"market", "marché", "marche"}

    PAIR_PATTERN = re.compile(r"([A-Z]{3,5})(?:[/\-]|)([A-Z]{3,5})")
    PRICE_PATTERN = re.compile(r"(?:at|à)\s+([0-9]+(?:[.,][0-9]+)?)", re.IGNORECASE)
    QUANTITY_PATTERN = re.compile(
        r"(?:buy|sell|ach(?:è|e)te|achat|vend(?:re|s)?)"  # action token
        r"[\s:]+"
        r"(?:[a-zA-Z]+\s+)?"  # optional filler words
        r"([0-9]+(?:[.,][0-9]+)?)",
        re.IGNORECASE,
    )

    def parse(self, message: str) -> OrderInstruction:
        normalized = message.strip()
        if not normalized:
            raise OrderParserError("The instruction message is empty.")

        lower_message = normalized.lower()
        side = self._extract_side(lower_message)
        order_type = self._extract_order_type(lower_message)
        pair = self._extract_pair(normalized)
        quantity = self._extract_quantity(lower_message)
        price = self._extract_price(lower_message) if order_type == "limit" else None

        if order_type == "limit" and price is None:
            raise OrderParserError(
                "No limit price found in the instruction while a limit order was requested."
            )

        return OrderInstruction(side=side, pair=pair, quantity=quantity, order_type=order_type, price=price)

    def _extract_side(self, message: str) -> str:
        for token in self.BUY_TOKENS:
            if token in message:
                return "buy"
        for token in self.SELL_TOKENS:
            if token in message:
                return "sell"
        raise OrderParserError("Could not determine whether the order is a buy or sell.")

    def _extract_order_type(self, message: str) -> str:
        for token in self.LIMIT_TOKENS:
            if token in message:
                return "limit"
        for token in self.MARKET_TOKENS:
            if token in message:
                return "market"
        # Default to market order if not explicitly mentioned.
        return "market"

    def _extract_pair(self, message: str) -> str:
        match = self.PAIR_PATTERN.search(message.upper())
        if not match:
            raise OrderParserError("No trading pair detected in the instruction.")

        base, quote = match.groups()
        return f"{base}_{quote}"

    def _extract_price(self, message: str) -> Optional[float]:
        match = self.PRICE_PATTERN.search(message)
        if not match:
            return None
        return float(match.group(1).replace(",", "."))

    def _extract_quantity(self, message: str) -> float:
        match = self.QUANTITY_PATTERN.search(message)
        if not match:
            raise OrderParserError("No quantity detected in the instruction.")
        return float(match.group(1).replace(",", "."))


__all__ = ["OrderParser", "OrderParserError", "OrderInstruction"]
