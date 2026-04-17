"""Tests for AdData dataclass — construction, API parsing, serialization."""
from facebook_ads_scraper.models import AdData


def test_from_api_full():
    raw = {
        "id": "1",
        "name": "Hero ad",
        "adset": {"id": "10", "name": "EU Prospecting"},
        "campaign": {"id": "100", "name": "Q2 Prospecting"},
        "creative": {"id": "1000", "name": "Video v3"},
    }
    ad = AdData.from_api(raw)
    assert ad.ad_id == "1"
    assert ad.ad_name == "Hero ad"
    assert ad.adset_id == "10"
    assert ad.adset_name == "EU Prospecting"
    assert ad.campaign_id == "100"
    assert ad.campaign_name == "Q2 Prospecting"
    assert ad.creative_id == "1000"
    assert ad.creative_name == "Video v3"


def test_from_api_missing_nested():
    """Missing nested fields should default to empty string, not blow up."""
    ad = AdData.from_api({"id": "1", "name": "Orphan"})
    assert ad.ad_id == "1"
    assert ad.adset_id == ""
    assert ad.campaign_name == ""
    assert ad.creative_id == ""


def test_from_api_fully_empty():
    ad = AdData.from_api({})
    for value in ad.to_dict().values():
        assert value == ""


def test_to_dict_round_trip():
    raw = {
        "id": "1",
        "name": "Hero",
        "adset": {"id": "10", "name": "EU"},
        "campaign": {"id": "100", "name": "Q2"},
        "creative": {"id": "1000", "name": "v3"},
    }
    ad = AdData.from_api(raw)
    d = ad.to_dict()
    assert d["ad_id"] == "1"
    assert d["campaign_name"] == "Q2"
    assert len(d) == 8  # all fields present
