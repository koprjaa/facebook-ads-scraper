# Facebook Ads Library Scraper

A Python tool for scraping Facebook Ads data using the Facebook Marketing API.

## Features

- Fetches ad data from Facebook Marketing API
- Processes and structures ad information
- Saves data to JSON format
- Comprehensive logging
- Environment variable configuration
- Error handling and validation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
export FACEBOOK_ACCESS_TOKEN="your_access_token_here"
export FACEBOOK_AD_ACCOUNT_ID="act_8204315166350573"
export FACEBOOK_ADS_LIMIT="100"
export FACEBOOK_ADS_OUTPUT_FILE="processed_ads.json"
export FACEBOOK_ADS_LOG_LEVEL="INFO"
export FACEBOOK_ADS_TIMEOUT="30"
```

## Usage

Run the scraper:
```bash
python fb_ad_lib_scraper.py
```

## Configuration

The scraper uses the following environment variables:

- `FACEBOOK_ACCESS_TOKEN`: Facebook API access token (required)
- `FACEBOOK_AD_ACCOUNT_ID`: Facebook ad account ID (default: act_8204315166350573)
- `FACEBOOK_ADS_LIMIT`: Maximum number of ads to fetch (default: 100)
- `FACEBOOK_ADS_OUTPUT_FILE`: Output file path (default: processed_ads.json)
- `FACEBOOK_ADS_LOG_LEVEL`: Logging level (default: INFO)
- `FACEBOOK_ADS_TIMEOUT`: Request timeout in seconds (default: 30)

## Output

The scraper generates:
- `processed_ads.json`: Structured ad data
- `facebook_ads_scraper.log`: Application logs

## Data Structure

Each ad entry contains:
- `ad_id`: Facebook ad ID
- `ad_name`: Ad name
- `adset_id`: Ad set ID
- `adset_name`: Ad set name
- `campaign_id`: Campaign ID
- `campaign_name`: Campaign name
- `creative_id`: Creative ID
- `creative_name`: Creative name
