#!/usr/bin/env python3
"""Programmatic usage of the Facebook Ads scraper as a library."""

from facebook_ads_scraper import AdData, FacebookAdsClient, FacebookAdsError, Settings


def main() -> int:
    settings = Settings.from_env()
    try:
        settings.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Set FACEBOOK_ACCESS_TOKEN and FACEBOOK_AD_ACCOUNT_ID environment variables.")
        return 2

    client = FacebookAdsClient(settings)
    try:
        # Stream ads as they arrive — useful for large accounts
        print("Streaming ads (first 5):")
        for i, raw in enumerate(client.iter_ads(limit=5)):
            ad = AdData.from_api(raw)
            print(f"  [{i + 1}] {ad.ad_name}  /  {ad.campaign_name}  /  {ad.adset_name}")

        # Or fetch everything
        print("\nFetching all ads (no limit)...")
        all_raw = client.fetch_all()
        print(f"Total: {len(all_raw)}")

    except FacebookAdsError as e:
        print(f"API error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
