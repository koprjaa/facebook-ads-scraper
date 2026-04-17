"""Facebook Graph Marketing API client with pagination, Bearer auth, and token scrubbing.

Design goals:
- Access token never leaks into log lines, error messages, or tracebacks.
- Transparent pagination via `paging.next` cursor.
- No module-level state; consumers construct `FacebookAdsClient(settings)`.
"""
from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlencode

import requests

from facebook_ads_scraper.config import Settings

_ACCESS_TOKEN_PATTERN = re.compile(r"([?&])access_token=[^&\s]*", re.IGNORECASE)


class FacebookAdsError(Exception):
    """Raised for any Graph API error or request failure (with the token scrubbed)."""


def _scrub_token(message: str) -> str:
    """Replace any `access_token=<value>` in a string with `access_token=REDACTED`."""
    return _ACCESS_TOKEN_PATTERN.sub(r"\1access_token=REDACTED", message)


class FacebookAdsClient:
    """Thin wrapper around `GET /{ad_account}/ads` with pagination."""

    FIELDS = "id,name,adset{id,name},campaign{id,name},creative{id,name}"

    def __init__(self, settings: Settings, logger: logging.Logger | None = None) -> None:
        if not settings.access_token:
            raise ValueError("settings.access_token is required")
        self.settings = settings
        self.logger = logger or logging.getLogger(__name__)
        self._session = requests.Session()
        # Bearer header — keeps the token out of query-string logs on the FB side too.
        self._session.headers.update(
            {
                "Authorization": f"Bearer {settings.access_token}",
                "Accept": "application/json",
            }
        )

    @property
    def endpoint(self) -> str:
        return (
            f"https://graph.facebook.com/{self.settings.api_version}"
            f"/{self.settings.ad_account_id}/ads"
        )

    def iter_ads(self, limit: int | None = None) -> Iterator[dict[str, Any]]:
        """Yield raw ad dicts, following `paging.next` until exhausted or `limit` reached.

        `limit` here is a soft global cap; the per-request page size comes from
        `settings.limit`. Set `limit=None` to fetch everything available.
        """
        fetched = 0
        url: str | None = self.endpoint
        params: dict[str, Any] | None = {
            "fields": self.FIELDS,
            "limit": self.settings.limit,
        }

        while url:
            self.logger.info(
                f"GET {url if params is None else url + '?' + urlencode(params)} (fetched so far: {fetched})"
            )
            try:
                response = self._session.get(
                    url, params=params, timeout=self.settings.timeout
                )
            except requests.RequestException as e:
                raise FacebookAdsError(_scrub_token(f"Request failed: {e}")) from None

            if response.status_code >= 400:
                self._raise_api_error(response)

            try:
                data = response.json()
            except ValueError as e:
                raise FacebookAdsError(f"Invalid JSON response: {e}") from None

            page = data.get("data", [])
            for ad in page:
                yield ad
                fetched += 1
                if limit is not None and fetched >= limit:
                    return

            # Pagination — subsequent pages use absolute URL from `paging.next`,
            # so we must drop params on the follow-up call.
            next_url = data.get("paging", {}).get("next")
            if next_url:
                url = next_url
                params = None
            else:
                url = None

        self.logger.info(f"Fetched {fetched} ads in total")

    def fetch_all(self, limit: int | None = None) -> list[dict[str, Any]]:
        """Collect all ads from `iter_ads` into a list."""
        return list(self.iter_ads(limit=limit))

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _raise_api_error(self, response: requests.Response) -> None:
        """Parse Graph API error body and raise FacebookAdsError with a scrubbed message."""
        try:
            body = response.json()
            err = body.get("error", {})
            message = err.get("message") or body
        except ValueError:
            message = response.text[:500]

        safe_url = _scrub_token(response.url)
        raise FacebookAdsError(
            f"Graph API returned HTTP {response.status_code} for {safe_url}: {message}"
        )
