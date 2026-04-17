#!/usr/bin/env python3
"""Thin entry shim for backwards compatibility with `python run.py`."""
import sys

from facebook_ads_scraper.cli import main

if __name__ == "__main__":
    sys.exit(main())
