# facebook-ads-scraper

**Minimal Python client that pulls your own Facebook Ad Account ads (+ adset, campaign, creative metadata) from the Graph Marketing API and dumps them as JSON. Pagination, Bearer auth, token scrubbing in error paths.**

![python](https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![license](https://img.shields.io/badge/license-MIT-A31F34?style=flat-square)
![status](https://img.shields.io/badge/status-active-22863A?style=flat-square)
![ruff](https://img.shields.io/badge/lint-ruff-D7FF64?style=flat-square)
![pytest](https://img.shields.io/badge/test-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![requests](https://img.shields.io/badge/requests-2.31+-000?style=flat-square)
![graph-api](https://img.shields.io/badge/Graph_API-v20.0-1877F2?style=flat-square&logo=facebook&logoColor=white)

The Meta Ads Library UI is fine for browsing. But once you want your ads joined to your campaigns and ad sets in a tidy JSON, the UI falls apart and the CSV export is lossy. This is a small scraper that hits the Graph Marketing API directly with a long-lived access token and writes a clean, structured JSON — handling pagination transparently, using a Bearer header (token never in query strings), and scrubbing the token from error messages so it can't leak through logs.

## Run

```bash
uv venv
uv pip install -e .

export FACEBOOK_ACCESS_TOKEN="EAAB...your_long_lived_token..."
export FACEBOOK_AD_ACCOUNT_ID="act_1234567890"

fb-ads-scraper                      # install-provided entry point
# or equivalently:
python -m facebook_ads_scraper
python run.py                       # backwards-compat shim
```

## CLI flags

| flag | effect |
|------|--------|
| `--output <path>` | override `FACEBOOK_ADS_OUTPUT_FILE` |
| `--limit <n>` | global cap on total ads fetched (default: no cap — pagination continues until `paging.next` is exhausted) |
| `--page-size <n>` | per-request page size (default: 100; overrides `FACEBOOK_ADS_LIMIT`) |
| `--log-level <level>` | DEBUG / INFO / WARNING / ERROR |

## Environment variables

| variable | required | default | purpose |
|----------|----------|---------|---------|
| `FACEBOOK_ACCESS_TOKEN` | ✓ | — | Graph API access token (long-lived preferred) |
| `FACEBOOK_AD_ACCOUNT_ID` | ✓ | — | Account ID, must start with `act_` |
| `FACEBOOK_ADS_LIMIT` | — | 100 | per-request page size |
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
from facebook_ads_scraper import AdData, FacebookAdsClient, Settings

settings = Settings.from_env()
settings.validate()

client = FacebookAdsClient(settings)

# Streaming — useful for large accounts
for raw in client.iter_ads(limit=1000):
    ad = AdData.from_api(raw)
    print(ad.ad_name, "→", ad.campaign_name)

# Or collect everything
ads = [AdData.from_api(r) for r in client.fetch_all()]
```

See [`examples/example_usage.py`](examples/example_usage.py) for a runnable script.

## Architecture

```
src/facebook_ads_scraper/
├── config.py      Settings dataclass + env overrides
├── client.py      FacebookAdsClient (pagination, Bearer auth, token scrubbing)
├── models.py      AdData dataclass + from_api() parser
├── cli.py         argparse + main
├── __main__.py    python -m facebook_ads_scraper
└── __init__.py    re-exports

tests/             pytest (config, models, client w/ responses mock) — 26 tests
.github/workflows/ci.yml   ruff + pytest × 3.10/3.11/3.12 × Linux/Windows
pyproject.toml     modern packaging with fb-ads-scraper entry point
run.py             backwards-compat shim
```

## Security notes

- **Bearer header, not query string.** The token travels in `Authorization: Bearer <token>` so Meta's reverse proxies don't accidentally log it.
- **Error messages scrub the token.** If the Graph API returns HTTP 4xx/5xx and includes the request URL, the client pattern-matches `?access_token=…` (and `&access_token=…`) and replaces the value with `REDACTED` before raising `FacebookAdsError`. Tracebacks and logs won't carry the secret.
- **No `.env` committed.** Put credentials in `.env` at repo root (gitignored by default).

## Getting a token

Tokens from the [Graph API Explorer](https://developers.facebook.com/tools/explorer/) expire in ~1 hour. For an unattended scraper you want a **long-lived user access token**:

1. Create a Facebook app under [developers.facebook.com/apps](https://developers.facebook.com/apps).
2. In Graph API Explorer, request the `ads_read` permission and generate a short-lived token.
3. Exchange it for a long-lived one (60-day validity):
   ```
   GET https://graph.facebook.com/v20.0/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id=APP_ID
       &client_secret=APP_SECRET
       &fb_exchange_token=SHORT_LIVED_TOKEN
   ```
4. For tokens that never expire, convert the long-lived token to a **system user** on a Business Manager account.

## Development

```bash
uv venv
uv pip install -e ".[dev]"
pytest -q            # 26 tests
ruff check .
```

## Known limits

- **Single account per run.** Fetches one `FACEBOOK_AD_ACCOUNT_ID` at a time. Wrap in a loop for multi-account pulls.
- **Ad Library (public) API is different.** This hits the **Marketing API** (your own ads). For searching *other companies'* political/social ads (public library), you need the `ads_archive` endpoint with different permissions.
- **No insights fields.** Fetches metadata only (IDs, names). Adding spend/impressions/CTR means extending `FacebookAdsClient.FIELDS` and `AdData`.

## License

[MIT](LICENSE)
