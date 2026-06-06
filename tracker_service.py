from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from database import InventoryItem, PriceHistory, PriceAlert, InventorySnapshot
from steam_api import SteamAPIClient
from price_service import PriceService
from config import settings

logger = logging.getLogger(__name__)


class TrackerService:
    """Main service for tracking CS2 inventory and prices."""

    def __init__(self, db: Session):
        self.db = db
        self.steam_client = SteamAPIClient()
        self.price_service = PriceService()

    async def sync_inventory(self) -> Dict:
        """
        Sync inventory from Steam and update database.
        Returns summary of sync operation.
        """
        logger.info("Starting inventory sync...")

        # Fetch inventory from Steam
        steam_items = await self.steam_client.get_inventory_async()

        if not steam_items:
            logger.warning("No items fetched from Steam")
            return {"success": False, "message": "Failed to fetch inventory from Steam"}

        added_count = 0
        updated_count = 0

        for steam_item in steam_items:
            # Check if item already exists
            existing_item = self.db.query(InventoryItem).filter(
                InventoryItem.asset_id == steam_item["asset_id"]
            ).first()

            if existing_item:
                # Update existing item
                existing_item.name = steam_item["name"]
                existing_item.market_hash_name = steam_item["market_hash_name"]
                existing_item.type = steam_item["type"]
                existing_item.rarity = steam_item["rarity"]
                existing_item.exterior = steam_item["exterior"]
                existing_item.updated_at = datetime.utcnow()
                updated_count += 1
            else:
                # Add new item
                new_item = InventoryItem(
                    asset_id=steam_item["asset_id"],
                    class_id=steam_item["class_id"],
                    instance_id=steam_item["instance_id"],
                    name=steam_item["name"],
                    market_hash_name=steam_item["market_hash_name"],
                    type=steam_item["type"],
                    rarity=steam_item["rarity"],
                    exterior=steam_item["exterior"],
                )
                self.db.add(new_item)
                added_count += 1

        self.db.commit()

        logger.info(f"Inventory sync complete: {added_count} added, {updated_count} updated")

        return {
            "success": True,
            "added": added_count,
            "updated": updated_count,
            "total": len(steam_items)
        }

    async def update_prices(self) -> Dict:
        """
        Update prices for all marketable items in inventory.
        Returns summary of price update operation.
        """
        logger.info("Starting price update...")

        # Get all items that need price updates
        items = self.db.query(InventoryItem).filter(
            InventoryItem.market_hash_name.isnot(None)
        ).all()

        if not items:
            return {"success": False, "message": "No items to update"}

        # Collect unique market names
        market_names = list(set([item.market_hash_name for item in items if item.market_hash_name]))

        # Fetch prices
        prices = await self.price_service.get_bulk_prices(market_names)

        updated_count = 0
        alert_count = 0

        for item in items:
            if not item.market_hash_name or item.market_hash_name not in prices:
                continue

            price_data = prices[item.market_hash_name]
            new_price = price_data.get("median_price") or price_data.get("lowest_price")

            if new_price is None:
                continue

            old_price = item.current_price

            # Update item price
            item.current_price = new_price
            item.last_price_update = datetime.utcnow()

            # Add to price history
            price_history = PriceHistory(
                item_id=item.id,
                price=new_price,
                timestamp=datetime.utcnow()
            )
            self.db.add(price_history)

            # Check for significant price changes and create alerts
            if old_price and old_price > 0:
                percentage_change = ((new_price - old_price) / old_price) * 100

                if abs(percentage_change) >= settings.price_alert_threshold:
                    alert_type = "gain" if percentage_change > 0 else "loss"
                    alert = PriceAlert(
                        item_id=item.id,
                        alert_type=alert_type,
                        percentage_change=percentage_change,
                        old_price=old_price,
                        new_price=new_price
                    )
                    self.db.add(alert)
                    alert_count += 1

            updated_count += 1

        self.db.commit()

        # Create inventory snapshot
        self._create_snapshot()

        logger.info(f"Price update complete: {updated_count} items updated, {alert_count} alerts created")

        return {
            "success": True,
            "updated": updated_count,
            "alerts": alert_count
        }

    def _create_snapshot(self):
        """Create a snapshot of current inventory value."""
        items = self.db.query(InventoryItem).all()

        total_value = sum(item.current_price or 0 for item in items)
        total_purchase_price = sum(item.purchase_price or 0 for item in items if item.purchase_price)
        total_profit_loss = total_value - total_purchase_price if total_purchase_price > 0 else None

        snapshot = InventorySnapshot(
            total_value=total_value,
            item_count=len(items),
            total_profit_loss=total_profit_loss
        )
        self.db.add(snapshot)
        self.db.commit()

    def get_inventory_summary(self) -> Dict:
        """Get summary of current inventory."""
        items = self.db.query(InventoryItem).all()

        total_value = sum(item.current_price or 0 for item in items)
        total_purchase_price = sum(item.purchase_price or 0 for item in items if item.purchase_price)
        total_profit_loss = total_value - total_purchase_price if total_purchase_price > 0 else 0

        return {
            "total_items": len(items),
            "total_value": round(total_value, 2),
            "total_purchase_price": round(total_purchase_price, 2),
            "total_profit_loss": round(total_profit_loss, 2),
            "profit_loss_percentage": round((total_profit_loss / total_purchase_price * 100), 2) if total_purchase_price > 0 else 0
        }

    def get_price_history(self, item_id: int, days: int = 30) -> List[Dict]:
        """Get price history for an item."""
        since = datetime.utcnow() - timedelta(days=days)

        history = self.db.query(PriceHistory).filter(
            PriceHistory.item_id == item_id,
            PriceHistory.timestamp >= since
        ).order_by(PriceHistory.timestamp).all()

        return [
            {
                "price": h.price,
                "timestamp": h.timestamp.isoformat()
            }
            for h in history
        ]

    def get_inventory_value_history(self, days: int = 30) -> List[Dict]:
        """Get total inventory value history."""
        since = datetime.utcnow() - timedelta(days=days)

        snapshots = self.db.query(InventorySnapshot).filter(
            InventorySnapshot.timestamp >= since
        ).order_by(InventorySnapshot.timestamp).all()

        return [
            {
                "total_value": s.total_value,
                "item_count": s.item_count,
                "profit_loss": s.total_profit_loss,
                "timestamp": s.timestamp.isoformat()
            }
            for s in snapshots
        ]

    def get_alerts(self, unread_only: bool = False) -> List[Dict]:
        """Get price alerts."""
        query = self.db.query(PriceAlert)

        if unread_only:
            query = query.filter(PriceAlert.is_read == False)

        alerts = query.order_by(PriceAlert.created_at.desc()).limit(100).all()

        result = []
        for alert in alerts:
            item = self.db.query(InventoryItem).get(alert.item_id)
            result.append({
                "id": alert.id,
                "item_name": item.name if item else "Unknown",
                "alert_type": alert.alert_type,
                "percentage_change": round(alert.percentage_change, 2),
                "old_price": alert.old_price,
                "new_price": alert.new_price,
                "is_read": alert.is_read,
                "created_at": alert.created_at.isoformat()
            })

        return result

    def mark_alert_read(self, alert_id: int):
        """Mark an alert as read."""
        alert = self.db.query(PriceAlert).get(alert_id)
        if alert:
            alert.is_read = True
            self.db.commit()

    def update_item_purchase_price(self, item_id: int, purchase_price: float):
        """Update the purchase price for an item."""
        item = self.db.query(InventoryItem).get(item_id)
        if item:
            item.purchase_price = purchase_price
            self.db.commit()
