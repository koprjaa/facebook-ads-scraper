"""Configuration module for Facebook Ads scraper."""

import os
from typing import Optional


class Config:
    """Configuration class for Facebook Ads scraper."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.access_token: Optional[str] = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.ad_account_id: str = os.getenv('FACEBOOK_AD_ACCOUNT_ID', 'act_8204315166350573')
        self.limit: int = int(os.getenv('FACEBOOK_ADS_LIMIT', '100'))
        self.output_file: str = os.getenv('FACEBOOK_ADS_OUTPUT_FILE', 'processed-ads.json')
        self.log_level: str = os.getenv('FACEBOOK_ADS_LOG_LEVEL', 'INFO')
        self.timeout: int = int(os.getenv('FACEBOOK_ADS_TIMEOUT', '30'))
    
    def validate(self) -> None:
        """
        Validate configuration.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not self.access_token:
            raise ValueError("FACEBOOK_ACCESS_TOKEN environment variable is required")
        
        if self.limit <= 0:
            raise ValueError("FACEBOOK_ADS_LIMIT must be a positive integer")
        
        if self.timeout <= 0:
            raise ValueError("FACEBOOK_ADS_TIMEOUT must be a positive integer")
        
        if not self.ad_account_id.startswith('act_'):
            raise ValueError("FACEBOOK_AD_ACCOUNT_ID must start with 'act_'")
