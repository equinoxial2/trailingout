"""Command line interface for the 3Commas instruction translator."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv

from .client import ThreeCommasClient, ThreeCommasConfig
from .parser import OrderParser, OrderParserError
from .translator import Translator

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOGGER = logging.getLogger(__name__)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", help="Instruction message to translate.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not perform HTTP requests, simply print the translated payload.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to an optional .env file containing API credentials.",
    )
    return parser


def load_config(dry_run: bool, env_file: Optional[str]) -> ThreeCommasConfig:
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()

    api_key = os.getenv("THREECOMMAS_API_KEY")
    api_secret = os.getenv("THREECOMMAS_API_SECRET")
    account_id = os.getenv("THREECOMMAS_ACCOUNT_ID")

    if not api_key or not api_secret or not account_id:
        missing = [
            name
            for name, value in [
                ("THREECOMMAS_API_KEY", api_key),
                ("THREECOMMAS_API_SECRET", api_secret),
                ("THREECOMMAS_ACCOUNT_ID", account_id),
            ]
            if not value
        ]
        raise SystemExit(
            "Missing environment variables: "
            + ", ".join(missing)
            + ". Configure them or provide an .env file."
        )

    return ThreeCommasConfig(
        api_key=api_key,
        api_secret=api_secret,
        account_id=int(account_id),
        dry_run=dry_run,
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if not args.message:
        parser.print_help()
        return 1

    config = load_config(args.dry_run, args.env_file)
    translator = Translator(client=ThreeCommasClient(config), parser=OrderParser())

    try:
        response = translator.translate_and_execute(args.message)
    except OrderParserError as exc:
        LOGGER.error("Failed to parse instruction: %s", exc)
        return 2
    except Exception as exc:  # pragma: no cover - guard around HTTP issues
        LOGGER.error("Failed to execute instruction: %s", exc)
        return 3

    if args.dry_run:
        LOGGER.info("Dry run response: %s", response)
    else:
        LOGGER.info("Trade created successfully: %s", response)
    return 0


if __name__ == "__main__":
    sys.exit(main())
