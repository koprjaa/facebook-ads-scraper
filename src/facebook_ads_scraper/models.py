"""Structured ad record."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class AdData:
    """One row of the scraped ads output."""

    ad_id: str
    ad_name: str
    adset_id: str
    adset_name: str
    campaign_id: str
    campaign_name: str
    creative_id: str
    creative_name: str

    @classmethod
    def from_api(cls, ad: dict[str, Any]) -> AdData:
        """Build an `AdData` from a raw Graph API ad dict (with nested `adset` / `campaign` / `creative`)."""
        return cls(
            ad_id=str(ad.get("id", "")),
            ad_name=str(ad.get("name", "")),
            adset_id=str(ad.get("adset", {}).get("id", "")),
            adset_name=str(ad.get("adset", {}).get("name", "")),
            campaign_id=str(ad.get("campaign", {}).get("id", "")),
            campaign_name=str(ad.get("campaign", {}).get("name", "")),
            creative_id=str(ad.get("creative", {}).get("id", "")),
            creative_name=str(ad.get("creative", {}).get("name", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
