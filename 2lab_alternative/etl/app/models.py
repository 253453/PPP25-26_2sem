from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import relationship

from datetime import datetime

from app.db import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    base_url = Column(String)

    items = relationship(
        "Item",
        back_populates="source"
    )


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    description = Column(String)

    price = Column(Float)

    source_id = Column(
        Integer,
        ForeignKey("sources.id")
    )

    source = relationship(
        "Source",
        back_populates="items"
    )

    events = relationship(
        "ItemEvent",
        back_populates="item"
    )


class ItemEvent(Base):
    __tablename__ = "item_events"

    id = Column(Integer, primary_key=True)

    event_type = Column(String)

    message = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    item_id = Column(
        Integer,
        ForeignKey("items.id")
    )

    item = relationship(
        "Item",
        back_populates="events"
    )