#!/usr/bin/env python3
"""Example usage of the Facebook Ads scraper."""

import os
import sys
from pathlib import Path

# Add parent directory to path to import the scraper
sys.path.append(str(Path(__file__).parent.parent))

from fb_ad_lib_scraper import FacebookAdsScraper
from config import Config


def main():
    """Example of how to use the Facebook Ads scraper programmatically."""
    
    # Load configuration
    config = Config()
    
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set the required environment variables.")
        return
    
    # Initialize scraper
    scraper = FacebookAdsScraper(
        access_token=config.access_token,
        ad_account_id=config.ad_account_id,
        limit=config.limit
    )
    
    try:
        # Run the scraper
        scraper.run(output_file="example-ads.json")
        print("Scraping completed successfully!")
        
        # You can also use individual methods
        print("\n--- Individual method usage ---")
        
        # Fetch ads
        ads_data = scraper.fetch_ads()
        print(f"Fetched {len(ads_data)} ads from API")
        
        # Process ads
        processed_ads = scraper.process_ads(ads_data)
        print(f"Processed {len(processed_ads)} ads")
        
        # Access individual ad data
        if processed_ads:
            first_ad = processed_ads[0]
            print(f"\nFirst ad example:")
            print(f"  ID: {first_ad.ad_id}")
            print(f"  Name: {first_ad.ad_name}")
            print(f"  Campaign: {first_ad.campaign_name}")
            print(f"  Ad Set: {first_ad.adset_name}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
