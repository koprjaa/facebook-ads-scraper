"""Tests for Settings — env loading, validation, type coercion."""
from pathlib import Path

import pytest

from facebook_ads_scraper.config import Settings


def test_defaults():
    s = Settings()
    assert s.access_token == ""
    assert s.ad_account_id == ""
    assert s.limit == 100
    assert s.timeout == 30
    assert s.log_level == "INFO"
    assert s.api_version == "v20.0"


def test_from_env_reads_all(monkeypatch):
    monkeypatch.setenv("FACEBOOK_ACCESS_TOKEN", "EAA-test")
    monkeypatch.setenv("FACEBOOK_AD_ACCOUNT_ID", "act_123")
    monkeypatch.setenv("FACEBOOK_ADS_LIMIT", "250")
    monkeypatch.setenv("FACEBOOK_ADS_OUTPUT_FILE", "out/custom.json")
    monkeypatch.setenv("FACEBOOK_ADS_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("FACEBOOK_ADS_TIMEOUT", "45")
    s = Settings.from_env()
    assert s.access_token == "EAA-test"
    assert s.ad_account_id == "act_123"
    assert s.limit == 250
    assert s.output_file == Path("out/custom.json")
    assert s.log_level == "DEBUG"
    assert s.timeout == 45


def test_validate_missing_token():
    s = Settings(access_token="", ad_account_id="act_1")
    with pytest.raises(ValueError, match="ACCESS_TOKEN"):
        s.validate()


def test_validate_missing_account():
    s = Settings(access_token="t", ad_account_id="")
    with pytest.raises(ValueError, match="AD_ACCOUNT_ID"):
        s.validate()


def test_validate_account_must_start_with_act():
    s = Settings(access_token="t", ad_account_id="123")
    with pytest.raises(ValueError, match="act_"):
        s.validate()


def test_validate_non_positive_limit():
    s = Settings(access_token="t", ad_account_id="act_1", limit=0)
    with pytest.raises(ValueError, match="LIMIT"):
        s.validate()


def test_validate_unknown_log_level():
    s = Settings(access_token="t", ad_account_id="act_1", log_level="LOUD")
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        s.validate()


def test_int_env_raises_on_garbage(monkeypatch):
    monkeypatch.setenv("FACEBOOK_ADS_LIMIT", "not-a-number")
    with pytest.raises(ValueError, match="must be an integer"):
        Settings.from_env()


def test_int_env_handles_empty_string_as_default(monkeypatch):
    monkeypatch.setenv("FACEBOOK_ADS_LIMIT", "")
    s = Settings.from_env()
    assert s.limit == 100  # default kept


def test_validate_all_good():
    s = Settings(access_token="t", ad_account_id="act_1", limit=10, timeout=5)
    s.validate()  # no raise
