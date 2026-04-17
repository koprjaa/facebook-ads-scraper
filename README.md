# facebook-ads-scraper

**Minimal Python client that pulls your own Facebook Ad Account ads (+ adset, campaign, creative metadata) from the Graph Marketing API and dumps them as JSON.**

![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-A31F34?style=flat-square)
![status](https://img.shields.io/badge/status-active-22863A?style=flat-square)
![requests](https://img.shields.io/badge/requests-2.31+-000?style=flat-square)
![graph-api](https://img.shields.io/badge/Graph_API-v20.0-1877F2?style=flat-square&logo=facebook&logoColor=white)

The Meta Ads Library UI is fine for browsing. But once you want your ads joined to your campaigns and ad sets in a tidy JSON, the UI falls apart and the CSV export is lossy. This is a ~200-line one-file scraper that hits the Graph Marketing API directly with a long-lived access token and writes a clean, structured JSON.

## Run

```bash
uv venv
uv pip install -r requirements.txt

export FACEBOOK_ACCESS_TOKEN="EAAB...your_long_lived_token..."
export FACEBOOK_AD_ACCOUNT_ID="act_1234567890"

python fb_ad_lib_scraper.py
# → processed-ads.json
```

## Environment variables

| variable | required | default | purpose |
|----------|----------|---------|---------|
| `FACEBOOK_ACCESS_TOKEN` | ✓ | — | Graph API access token (long-lived preferred) |
| `FACEBOOK_AD_ACCOUNT_ID` | ✓ | — | Account ID, must start with `act_` |
| `FACEBOOK_ADS_LIMIT` | — | 100 | max ads per request |
| `FACEBOOK_ADS_OUTPUT_FILE` | — | `processed-ads.json` | output path |
| `FACEBOOK_ADS_LOG_LEVEL` | — | INFO | DEBUG / INFO / WARNING / ERROR |
| `FACEBOOK_ADS_TIMEOUT` | — | 30 | HTTP timeout (s) |

## Output shape

```jsonc
[
  {
    "ad_id": "1234567890",
    "ad_name": "Summer Sale — Desktop Homepage Carousel",
    "adset_id": "2345678901",
    "adset_name": "EU – 25-44 – Lookalike 1%",
    "campaign_id": "3456789012",
    "campaign_name": "2026-Q2 Prospecting",
    "creative_id": "4567890123",
    "creative_name": "Hero video v3"
  },
  ...
]
```

## Programmatic use

```python
from fb_ad_lib_scraper import FacebookAdsScraper
from config import Config

config = Config()
config.validate()

scraper = FacebookAdsScraper(
    access_token=config.access_token,
    ad_account_id=config.ad_account_id,
    limit=config.limit,
)
ads = scraper.fetch_ads()          # raw list[dict] from Graph API
processed = scraper.process_ads(ads)  # list[AdData]
scraper.save_ads_to_file(processed, "custom.json")
```

See [`examples/example_usage.py`](examples/example_usage.py) for a runnable script.

## Getting a token

Tokens from the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) expire in ~1 hour. For an unattended scraper you want a **long-lived user access token**:

1. Create a Facebook app under [developers.facebook.com/apps](https://developers.facebook.com/apps).
2. In Graph API Explorer, request the `ads_read` permission and generate a short-lived token.
3. Exchange it for a long-lived one (60-day validity) via:
   ```
   GET https://graph.facebook.com/v20.0/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id=APP_ID
       &client_secret=APP_SECRET
       &fb_exchange_token=SHORT_LIVED_TOKEN
   ```
4. For tokens that never expire, convert the long-lived token to a **system user** on a Business Manager account.

## Known limits

- **Pagination not implemented** — currently caps at the `limit` value (default 100). For accounts with thousands of ads, add a `paging.next` follow loop.
- **Single account per run** — fetches one `FACEBOOK_AD_ACCOUNT_ID` at a time. Wrap the scraper in a loop for multi-account pulls.
- **Ad Library (public) API is different** — this hits the **Marketing API** (your own ads). For searching *other companies*' political/social ads (public library), you need the `ads_archive` endpoint with a different scope.

## License

[MIT](LICENSE)
