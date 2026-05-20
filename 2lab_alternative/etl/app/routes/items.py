from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException


from sqlalchemy.orm import Session

from app.db import get_db

from app.models import Item, Source

from app.schemas import (
    ItemCreate,
    ItemPatch,
    ItemResponse,
    SourceCreate, 
    SourceResponse
)

router = APIRouter(
    prefix="/items",
    tags=["Items"]
)


@router.get("/", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):

    return db.query(Item).all()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.query(Item)\
        .filter(Item.id == item_id)\
        .first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )

    return item


@router.post("/", response_model=ItemResponse)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    if item.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price must be greater than 0"
        )

    source = db.query(Source).filter(Source.id == item.source_id).first()

    if not source:
        raise HTTPException(
            status_code=400,
            detail="Source not found"
        )
    
    db_item = Item(**item.model_dump())

    db.add(db_item)

    db.commit()

    db.refresh(db_item)

    return db_item


@router.put("/{item_id}")
def replace_item(
    item_id: int,
    item_data: ItemCreate,
    db: Session = Depends(get_db)
):

    item = db.query(Item)\
        .filter(Item.id == item_id)\
        .first()

    if not item:
        raise HTTPException(404, "Item not found")

    for key, value in item_data.model_dump().items():
        setattr(item, key, value)

    db.commit()

    return item


@router.patch("/{item_id}")
def patch_item(
    item_id: int,
    item_data: ItemPatch,
    db: Session = Depends(get_db)
):

    item = db.query(Item)\
        .filter(Item.id == item_id)\
        .first()

    if not item:
        raise HTTPException(404, "Item not found")

    updates = item_data.model_dump(
        exclude_unset=True
    )

    for key, value in updates.items():
        setattr(item, key, value)

    db.commit()

    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):

    item = db.query(Item)\
        .filter(Item.id == item_id)\
        .first()

    if not item:
        raise HTTPException(404, "Item not found")

    db.delete(item)

    db.commit()

    return {
        "message": "Item deleted"
    }