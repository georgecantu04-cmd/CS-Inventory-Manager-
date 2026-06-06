import aiohttp
import requests
from typing import List, Dict, Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class SteamAPIClient:
    """Client for interacting with Steam API."""

    CS2_APP_ID = 730  # Counter-Strike 2 App ID

    def __init__(self, api_key: str = None, steam_id: str = None):
        self.api_key = api_key or settings.steam_api_key
        self.steam_id = steam_id or settings.steam_id
        self.base_url = "https://api.steampowered.com"

    async def get_inventory_async(self) -> List[Dict]:
        """
        Fetch CS2 inventory from Steam API asynchronously.
        Returns list of inventory items with their details.
        """
        url = f"https://steamcommunity.com/inventory/{self.steam_id}/{self.CS2_APP_ID}/2"
        params = {"l": "english", "count": 5000}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch inventory: {response.status}")
                        return []

                    data = await response.json()

                    if not data.get("success"):
                        logger.error("Steam API returned unsuccessful response")
                        return []

                    assets = data.get("assets", [])
                    descriptions = data.get("descriptions", [])

                    # Create a lookup dictionary for descriptions
                    desc_lookup = {
                        f"{desc['classid']}_{desc['instanceid']}": desc
                        for desc in descriptions
                    }

                    # Combine assets with their descriptions
                    inventory_items = []
                    for asset in assets:
                        key = f"{asset['classid']}_{asset['instanceid']}"
                        desc = desc_lookup.get(key, {})

                        item = {
                            "asset_id": asset.get("assetid"),
                            "class_id": asset.get("classid"),
                            "instance_id": asset.get("instanceid"),
                            "name": desc.get("name", "Unknown"),
                            "market_hash_name": desc.get("market_hash_name"),
                            "type": desc.get("type", "Unknown"),
                            "rarity": self._extract_rarity(desc.get("tags", [])),
                            "exterior": self._extract_exterior(desc.get("tags", [])),
                            "tradable": desc.get("tradable", 0) == 1,
                            "marketable": desc.get("marketable", 0) == 1,
                            "icon_url": desc.get("icon_url"),
                        }
                        inventory_items.append(item)

                    logger.info(f"Successfully fetched {len(inventory_items)} items from inventory")
                    return inventory_items

        except Exception as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return []

    def get_inventory(self) -> List[Dict]:
        """Synchronous version of get_inventory."""
        url = f"https://steamcommunity.com/inventory/{self.steam_id}/{self.CS2_APP_ID}/2"
        params = {"l": "english", "count": 5000}

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to fetch inventory: {response.status_code}")
                return []

            data = response.json()

            if not data.get("success"):
                logger.error("Steam API returned unsuccessful response")
                return []

            assets = data.get("assets", [])
            descriptions = data.get("descriptions", [])

            # Create a lookup dictionary for descriptions
            desc_lookup = {
                f"{desc['classid']}_{desc['instanceid']}": desc
                for desc in descriptions
            }

            # Combine assets with their descriptions
            inventory_items = []
            for asset in assets:
                key = f"{asset['classid']}_{asset['instanceid']}"
                desc = desc_lookup.get(key, {})

                item = {
                    "asset_id": asset.get("assetid"),
                    "class_id": asset.get("classid"),
                    "instance_id": asset.get("instanceid"),
                    "name": desc.get("name", "Unknown"),
                    "market_hash_name": desc.get("market_hash_name"),
                    "type": desc.get("type", "Unknown"),
                    "rarity": self._extract_rarity(desc.get("tags", [])),
                    "exterior": self._extract_exterior(desc.get("tags", [])),
                    "tradable": desc.get("tradable", 0) == 1,
                    "marketable": desc.get("marketable", 0) == 1,
                    "icon_url": desc.get("icon_url"),
                }
                inventory_items.append(item)

            logger.info(f"Successfully fetched {len(inventory_items)} items from inventory")
            return inventory_items

        except Exception as e:
            logger.error(f"Error fetching inventory: {str(e)}")
            return []

    def _extract_rarity(self, tags: List[Dict]) -> Optional[str]:
        """Extract rarity from item tags."""
        for tag in tags:
            if tag.get("category") == "Rarity":
                return tag.get("localized_tag_name")
        return None

    def _extract_exterior(self, tags: List[Dict]) -> Optional[str]:
        """Extract exterior (wear) from item tags."""
        for tag in tags:
            if tag.get("category") == "Exterior":
                return tag.get("localized_tag_name")
        return None

    async def get_player_summary(self) -> Optional[Dict]:
        """Get player summary information."""
        url = f"{self.base_url}/ISteamUser/GetPlayerSummaries/v0002/"
        params = {"key": self.api_key, "steamids": self.steam_id}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        players = data.get("response", {}).get("players", [])
                        return players[0] if players else None
        except Exception as e:
            logger.error(f"Error fetching player summary: {str(e)}")

        return None
