import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('facebook-ads-scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AdData:
    """Data class representing a Facebook ad."""
    ad_id: str
    ad_name: str
    adset_id: str
    adset_name: str
    campaign_id: str
    campaign_name: str
    creative_id: str
    creative_name: str


class FacebookAdsScraper:
    """Facebook Ads Library scraper for fetching and processing ad data."""
    
    def __init__(self, access_token: str, ad_account_id: str, limit: int = 100):
        """
        Initialize the Facebook Ads scraper.
        
        Args:
            access_token: Facebook API access token
            ad_account_id: Facebook ad account ID
            limit: Maximum number of ads to fetch
        """
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.limit = limit
        self.base_url = f'https://graph.facebook.com/v20.0/{ad_account_id}/ads'
        
        if not access_token:
            raise ValueError("Access token is required")
    
    def fetch_ads(self) -> List[Dict[str, Any]]:
        """
        Fetch ads from Facebook API.
        
        Returns:
            List of ad data dictionaries
            
        Raises:
            requests.RequestException: If API request fails
            ValueError: If API returns error response
        """
        params = {
            'access_token': self.access_token,
            'fields': 'id,name,adset{id,name},campaign{id,name},creative',
            'limit': self.limit
        }
        
        try:
            logger.info(f"Fetching ads from Facebook API (limit: {self.limit})")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            response_data = response.json()
            
            if 'data' in response_data:
                ads_count = len(response_data['data'])
                logger.info(f"Successfully fetched {ads_count} ads")
                return response_data['data']
            else:
                error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                logger.error(f"API error: {error_msg}")
                raise ValueError(f"Facebook API error: {error_msg}")
                
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid JSON response from Facebook API")
    
    def process_ads(self, ads_data: List[Dict[str, Any]]) -> List[AdData]:
        """
        Process raw ad data into structured AdData objects.
        
        Args:
            ads_data: Raw ad data from Facebook API
            
        Returns:
            List of processed AdData objects
        """
        processed_ads = []
        
        for ad in ads_data:
            try:
                processed_ad = AdData(
                    ad_id=ad.get('id', 'N/A'),
                    ad_name=ad.get('name', 'N/A'),
                    adset_id=ad.get('adset', {}).get('id', 'N/A'),
                    adset_name=ad.get('adset', {}).get('name', 'N/A'),
                    campaign_id=ad.get('campaign', {}).get('id', 'N/A'),
                    campaign_name=ad.get('campaign', {}).get('name', 'N/A'),
                    creative_id=ad.get('creative', {}).get('id', 'N/A'),
                    creative_name=ad.get('creative', {}).get('name', 'N/A')
                )
                processed_ads.append(processed_ad)
            except Exception as e:
                logger.warning(f"Failed to process ad {ad.get('id', 'unknown')}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_ads)} ads successfully")
        return processed_ads
    
    def save_ads_to_file(self, ads: List[AdData], output_file: str) -> None:
        """
        Save processed ads to JSON file.
        
        Args:
            ads: List of AdData objects to save
            output_file: Path to output file
        """
        # Convert AdData objects to dictionaries
        ads_dict = [
            {
                'ad_id': ad.ad_id,
                'ad_name': ad.ad_name,
                'adset_id': ad.adset_id,
                'adset_name': ad.adset_name,
                'campaign_id': ad.campaign_id,
                'campaign_name': ad.campaign_name,
                'creative_id': ad.creative_id,
                'creative_name': ad.creative_name
            }
            for ad in ads
        ]
        
        try:
            # Delete old report if it exists
            if Path(output_file).exists():
                Path(output_file).unlink()
                logger.info(f"Deleted old report: {output_file}")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(ads_dict, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Saved {len(ads)} ads to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save ads to file: {e}")
            raise
    
    def run(self, output_file: str = 'processed-ads.json') -> None:
        """
        Run the complete scraping process.
        
        Args:
            output_file: Path to output file for processed ads
        """
        try:
            logger.info("Starting Facebook Ads scraping process")
            
            # Fetch ads from API
            ads_data = self.fetch_ads()
            
            # Process ads
            processed_ads = self.process_ads(ads_data)
            
            # Save to file
            self.save_ads_to_file(processed_ads, output_file)
            
            logger.info("Facebook Ads scraping completed successfully")
            
        except Exception as e:
            logger.error(f"Scraping process failed: {e}")
            raise


def main():
    """Main function to run the Facebook Ads scraper."""
    try:
        # Load and validate configuration
        config = Config()
        config.validate()
        
        # Initialize and run scraper
        scraper = FacebookAdsScraper(
            access_token=config.access_token,
            ad_account_id=config.ad_account_id,
            limit=config.limit
        )
        scraper.run(output_file=config.output_file)
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        raise


if __name__ == "__main__":
    main()
