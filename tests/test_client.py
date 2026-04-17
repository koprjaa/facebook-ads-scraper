"""Tests for FacebookAdsClient — pagination, error handling, token scrubbing."""
import pytest
import responses

from facebook_ads_scraper.client import FacebookAdsClient, FacebookAdsError, _scrub_token
from facebook_ads_scraper.config import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings(
        access_token="EAA-test",
        ad_account_id="act_1",
        limit=2,
        timeout=5,
    )


# ----------------------------- token scrubbing -----------------------------


def test_scrub_token_query_param():
    url = "https://graph.facebook.com/v20.0/act_1/ads?access_token=EAAsecret&limit=100"
    assert "EAAsecret" not in _scrub_token(url)
    assert "access_token=REDACTED" in _scrub_token(url)


def test_scrub_token_preserves_other_params():
    url = "https://graph.facebook.com/v20.0/act_1/ads?limit=100&access_token=secret&fields=id"
    scrubbed = _scrub_token(url)
    assert "limit=100" in scrubbed
    assert "fields=id" in scrubbed
    assert "secret" not in scrubbed


def test_scrub_token_no_token_in_input():
    url = "https://graph.facebook.com/v20.0/act_1/ads?limit=100"
    assert _scrub_token(url) == url


def test_scrub_token_handles_token_as_first_param():
    # ?access_token=... (first param)
    url = "https://graph.facebook.com/v20.0/act_1/ads?access_token=secret&limit=100"
    scrubbed = _scrub_token(url)
    assert "secret" not in scrubbed
    assert "limit=100" in scrubbed


# ----------------------------- pagination -----------------------------


@responses.activate
def test_iter_ads_single_page(settings):
    responses.add(
        responses.GET,
        f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads",
        json={
            "data": [
                {"id": "1", "name": "Ad 1"},
                {"id": "2", "name": "Ad 2"},
            ]
        },
        status=200,
    )
    client = FacebookAdsClient(settings)
    ads = list(client.iter_ads())
    assert len(ads) == 2
    assert ads[0]["id"] == "1"


@responses.activate
def test_iter_ads_paginates(settings):
    base = f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads"
    next_url = f"{base}?after=cursor123"
    responses.add(
        responses.GET,
        base,
        json={
            "data": [{"id": "1", "name": "Ad 1"}, {"id": "2", "name": "Ad 2"}],
            "paging": {"next": next_url},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        next_url,
        json={"data": [{"id": "3", "name": "Ad 3"}]},
        status=200,
    )
    client = FacebookAdsClient(settings)
    ads = list(client.iter_ads())
    assert [ad["id"] for ad in ads] == ["1", "2", "3"]


@responses.activate
def test_iter_ads_respects_global_limit(settings):
    base = f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads"
    next_url = f"{base}?after=cursor123"
    responses.add(
        responses.GET,
        base,
        json={
            "data": [{"id": "1"}, {"id": "2"}],
            "paging": {"next": next_url},
        },
        status=200,
    )
    responses.add(
        responses.GET,
        next_url,
        json={"data": [{"id": "3"}, {"id": "4"}]},
        status=200,
    )
    client = FacebookAdsClient(settings)
    ads = list(client.iter_ads(limit=3))
    assert len(ads) == 3


# ----------------------------- error handling -----------------------------


@responses.activate
def test_api_error_raises_without_token_in_message(settings):
    base = f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads"
    responses.add(
        responses.GET,
        base,
        json={
            "error": {
                "message": "Invalid access token",
                "type": "OAuthException",
                "code": 190,
            }
        },
        status=400,
    )
    client = FacebookAdsClient(settings)
    with pytest.raises(FacebookAdsError) as exc_info:
        list(client.iter_ads())
    assert "EAA-test" not in str(exc_info.value)
    assert "HTTP 400" in str(exc_info.value)
    assert "Invalid access token" in str(exc_info.value)


@responses.activate
def test_network_failure_raises(settings):
    import requests

    base = f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads"
    responses.add(
        responses.GET,
        base,
        body=requests.ConnectionError("network down"),
    )
    client = FacebookAdsClient(settings)
    with pytest.raises(FacebookAdsError):
        list(client.iter_ads())


# ----------------------------- misc -----------------------------


def test_empty_access_token_rejected():
    settings = Settings(access_token="", ad_account_id="act_1")
    with pytest.raises(ValueError, match="access_token"):
        FacebookAdsClient(settings)


def test_bearer_header_is_set(settings):
    client = FacebookAdsClient(settings)
    assert client._session.headers["Authorization"] == f"Bearer {settings.access_token}"


def test_fetch_all_is_list(settings):
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            f"https://graph.facebook.com/{settings.api_version}/{settings.ad_account_id}/ads",
            json={"data": [{"id": "1"}, {"id": "2"}]},
            status=200,
        )
        client = FacebookAdsClient(settings)
        result = client.fetch_all()
        assert isinstance(result, list)
        assert len(result) == 2
