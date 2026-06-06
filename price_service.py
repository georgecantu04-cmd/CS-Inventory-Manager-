import aiohttp
import requests
from typing import Optional, Dict
from config import settings
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PriceService:
    """Service for fetching CS2 item prices from Steam Market."""

    def __init__(self):
        self.base_url = "https://steamcommunity.com/market/priceoverview/"
        self.app_id = 730  # CS2 App ID
        # Rate limiting: Steam allows ~20 requests per minute
        self.request_delay = 3  # seconds between requests
        self.last_request_time = None

    async def get_item_price_async(self, market_hash_name: str, currency: int = 1) -> Optional[Dict]:
        """
        Fetch current market price for an item asynchronously.

        Args:
            market_hash_name: The market hash name of the item
            currency: Currency code (1 = USD, 3 = EUR, etc.)

        Returns:
            Dict with price information or None if failed
        """
        if not market_hash_name:
            return None

        # Rate limiting
        await self._rate_limit()

        params = {
            "appid": self.app_id,
            "currency": currency,
            "market_hash_name": market_hash_name
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch price for {market_hash_name}: {response.status}")
                        return None

                    data = await response.json()

                    if not data.get("success"):
                        logger.warning(f"Unsuccessful price fetch for {market_hash_name}")
                        return None

                    # Parse prices (remove currency symbols and convert to float)
                    lowest_price = self._parse_price(data.get("lowest_price"))
                    median_price = self._parse_price(data.get("median_price"))
                    volume = data.get("volume", "0").replace(",", "")

                    return {
                        "lowest_price": lowest_price,
                        "median_price": median_price,
                        "volume": int(volume) if volume.isdigit() else 0,
                        "market_hash_name": market_hash_name,
                        "timestamp": datetime.utcnow()
                    }

        except Exception as e:
            logger.error(f"Error fetching price for {market_hash_name}: {str(e)}")
            return None

    def get_item_price(self, market_hash_name: str, currency: int = 1) -> Optional[Dict]:
        """Synchronous version of get_item_price."""
        if not market_hash_name:
            return None

        params = {
            "appid": self.app_id,
            "currency": currency,
            "market_hash_name": market_hash_name
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Failed to fetch price for {market_hash_name}: {response.status_code}")
                return None

            data = response.json()

            if not data.get("success"):
                logger.warning(f"Unsuccessful price fetch for {market_hash_name}")
                return None

            # Parse prices
            lowest_price = self._parse_price(data.get("lowest_price"))
            median_price = self._parse_price(data.get("median_price"))
            volume = data.get("volume", "0").replace(",", "")

            return {
                "lowest_price": lowest_price,
                "median_price": median_price,
                "volume": int(volume) if volume.isdigit() else 0,
                "market_hash_name": market_hash_name,
                "timestamp": datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Error fetching price for {market_hash_name}: {str(e)}")
            return None

    def _parse_price(self, price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float, handling different currency formats."""
        if not price_str:
            return None

        try:
            # Remove currency symbols and spaces
            clean_price = price_str.replace("$", "").replace("€", "").replace("£", "")
            clean_price = clean_price.replace(",", "").strip()
            return float(clean_price)
        except (ValueError, AttributeError):
            return None

    async def _rate_limit(self):
        """Implement rate limiting for API requests."""
        if self.last_request_time:
            elapsed = (datetime.utcnow() - self.last_request_time).total_seconds()
            if elapsed < self.request_delay:
                await asyncio.sleep(self.request_delay - elapsed)

        self.last_request_time = datetime.utcnow()

    async def get_bulk_prices(self, market_hash_names: list[str]) -> Dict[str, Dict]:
        """
        Fetch prices for multiple items with rate limiting.

        Args:
            market_hash_names: List of market hash names

        Returns:
            Dictionary mapping market_hash_name to price data
        """
        results = {}

        for name in market_hash_names:
            if name:
                price_data = await self.get_item_price_async(name)
                if price_data:
                    results[name] = price_data

        return results
