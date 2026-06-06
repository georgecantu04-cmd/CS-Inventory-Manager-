from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import settings

# Database setup
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class InventoryItem(Base):
    """Represents a CS2 item in the user's inventory."""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String, unique=True, index=True)
    class_id = Column(String, index=True)
    instance_id = Column(String)

    # Item details
    name = Column(String, index=True)
    market_hash_name = Column(String)
    type = Column(String)
    rarity = Column(String)
    exterior = Column(String, nullable=True)

    # Pricing
    purchase_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    last_price_update = Column(DateTime, nullable=True)

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="item", cascade="all, delete-orphan")


class PriceHistory(Base):
    """Historical price data for inventory items."""
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    item = relationship("InventoryItem", back_populates="price_history")


class PriceAlert(Base):
    """Price alerts for significant changes."""
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    alert_type = Column(String)  # 'gain' or 'loss'
    percentage_change = Column(Float)
    old_price = Column(Float)
    new_price = Column(Float)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class InventorySnapshot(Base):
    """Snapshot of total inventory value over time."""
    __tablename__ = "inventory_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    total_value = Column(Float)
    item_count = Column(Integer)
    total_profit_loss = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


def init_db():
    """Initialize the database and create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
