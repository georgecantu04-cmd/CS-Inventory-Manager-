from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from database import init_db, get_db, InventoryItem, PriceAlert
from tracker_service import TrackerService
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CS2 Inventory Tracker",
    description="Track your Counter-Strike 2 inventory value and price changes",
    version="1.0.0"
)

# Pydantic models for API
class SyncResponse(BaseModel):
    success: bool
    message: str = None
    added: int = None
    updated: int = None
    total: int = None


class PriceUpdateResponse(BaseModel):
    success: bool
    message: str = None
    updated: int = None
    alerts: int = None


class InventorySummary(BaseModel):
    total_items: int
    total_value: float
    total_purchase_price: float
    total_profit_loss: float
    profit_loss_percentage: float


class ItemResponse(BaseModel):
    id: int
    name: str
    market_hash_name: Optional[str]
    type: str
    rarity: Optional[str]
    exterior: Optional[str]
    current_price: Optional[float]
    purchase_price: Optional[float]
    profit_loss: Optional[float]
    last_price_update: Optional[datetime]


class UpdatePurchasePriceRequest(BaseModel):
    purchase_price: float


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and start background scheduler."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

    # Start background scheduler for periodic price updates
    scheduler = AsyncIOScheduler()

    async def scheduled_price_update():
        """Background task to update prices periodically."""
        logger.info("Running scheduled price update...")
        db = next(get_db())
        try:
            tracker = TrackerService(db)
            result = await tracker.update_prices()
            logger.info(f"Scheduled price update completed: {result}")
        except Exception as e:
            logger.error(f"Error in scheduled price update: {str(e)}")
        finally:
            db.close()

    # Schedule price updates based on configuration
    scheduler.add_job(
        scheduled_price_update,
        'interval',
        minutes=settings.update_interval_minutes,
        id='price_update_job'
    )

    scheduler.start()
    logger.info(f"Scheduler started - price updates every {settings.update_interval_minutes} minutes")


# API Endpoints
@app.get("/")
async def read_root():
    """Serve the main HTML page."""
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/api/sync", response_model=SyncResponse)
async def sync_inventory(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Sync inventory from Steam API."""
    try:
        tracker = TrackerService(db)
        result = await tracker.sync_inventory()

        if result["success"]:
            # Update prices after sync in background
            background_tasks.add_task(update_prices_task, db)

        return result
    except Exception as e:
        logger.error(f"Error syncing inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update-prices", response_model=PriceUpdateResponse)
async def update_prices(db: Session = Depends(get_db)):
    """Manually trigger price update for all items."""
    try:
        tracker = TrackerService(db)
        result = await tracker.update_prices()
        return result
    except Exception as e:
        logger.error(f"Error updating prices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_prices_task(db: Session):
    """Background task for updating prices."""
    try:
        tracker = TrackerService(db)
        await tracker.update_prices()
    except Exception as e:
        logger.error(f"Error in background price update: {str(e)}")


@app.get("/api/summary", response_model=InventorySummary)
async def get_summary(db: Session = Depends(get_db)):
    """Get inventory summary."""
    tracker = TrackerService(db)
    return tracker.get_inventory_summary()


@app.get("/api/items", response_model=List[ItemResponse])
async def get_items(db: Session = Depends(get_db)):
    """Get all inventory items."""
    items = db.query(InventoryItem).all()

    result = []
    for item in items:
        profit_loss = None
        if item.current_price and item.purchase_price:
            profit_loss = item.current_price - item.purchase_price

        result.append({
            "id": item.id,
            "name": item.name,
            "market_hash_name": item.market_hash_name,
            "type": item.type,
            "rarity": item.rarity,
            "exterior": item.exterior,
            "current_price": item.current_price,
            "purchase_price": item.purchase_price,
            "profit_loss": profit_loss,
            "last_price_update": item.last_price_update
        })

    return result


@app.get("/api/items/{item_id}/price-history")
async def get_item_price_history(
    item_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get price history for a specific item."""
    tracker = TrackerService(db)
    return tracker.get_price_history(item_id, days)


@app.get("/api/inventory-history")
async def get_inventory_history(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get total inventory value history."""
    tracker = TrackerService(db)
    return tracker.get_inventory_value_history(days)


@app.get("/api/alerts")
async def get_alerts(
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get price alerts."""
    tracker = TrackerService(db)
    return tracker.get_alerts(unread_only)


@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as read."""
    tracker = TrackerService(db)
    tracker.mark_alert_read(alert_id)
    return {"success": True}


@app.put("/api/items/{item_id}/purchase-price")
async def update_purchase_price(
    item_id: int,
    request: UpdatePurchasePriceRequest,
    db: Session = Depends(get_db)
):
    """Update the purchase price for an item."""
    tracker = TrackerService(db)
    tracker.update_item_purchase_price(item_id, request.purchase_price)
    return {"success": True}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
