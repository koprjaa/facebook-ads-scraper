"""CLI entry point."""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from facebook_ads_scraper.client import FacebookAdsClient, FacebookAdsError
from facebook_ads_scraper.config import Settings
from facebook_ads_scraper.models import AdData


def _setup_logging(level: str) -> logging.Logger:
    logger = logging.getLogger("facebook_ads_scraper")
    logger.setLevel(getattr(logging, level.upper()))
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(handler)
    return logger


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fb-ads-scraper",
        description="Fetch Facebook Ad Account ads via the Graph Marketing API and write them to JSON.",
    )
    parser.add_argument("--output", help="Output JSON file (overrides FACEBOOK_ADS_OUTPUT_FILE)")
    parser.add_argument(
        "--limit",
        type=int,
        help="Global cap on the number of ads to fetch (default: unlimited; pagination handled automatically)",
    )
    parser.add_argument("--page-size", type=int, help="Per-request page size (overrides FACEBOOK_ADS_LIMIT)")
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (overrides FACEBOOK_ADS_LOG_LEVEL)",
    )
    return parser


def _write_json(ads: list[AdData], output_file: Path, logger: logging.Logger) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8") as f:
        json.dump([ad.to_dict() for ad in ads], f, ensure_ascii=False, indent=4)
    logger.info(f"Wrote {len(ads)} ads to {output_file}")


def main() -> int:
    args = _build_parser().parse_args()

    settings = Settings.from_env()
    if args.page_size is not None:
        settings.limit = args.page_size
    if args.output is not None:
        settings.output_file = Path(args.output)
    if args.log_level is not None:
        settings.log_level = args.log_level

    logger = _setup_logging(settings.log_level)

    try:
        settings.validate()
    except ValueError as e:
        logger.error(str(e))
        return 2

    client = FacebookAdsClient(settings, logger=logger)
    try:
        raw_ads = client.fetch_all(limit=args.limit)
    except FacebookAdsError as e:
        logger.error(str(e))
        return 1

    ads = [AdData.from_api(ad) for ad in raw_ads]
    logger.info(f"Processed {len(ads)} ads")

    _write_json(ads, settings.output_file, logger)
    return 0


if __name__ == "__main__":
    sys.exit(main())
