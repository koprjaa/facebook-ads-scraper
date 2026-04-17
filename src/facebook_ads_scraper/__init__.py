"""Facebook Ad Account scraper — Graph Marketing API to JSON."""
from facebook_ads_scraper.client import FacebookAdsClient, FacebookAdsError
from facebook_ads_scraper.config import Settings
from facebook_ads_scraper.models import AdData

__version__ = "0.2.0"

__all__ = ["AdData", "FacebookAdsClient", "FacebookAdsError", "Settings"]
