from pydantic import BaseModel, Field
from typing import Optional


class ItemCreate(BaseModel):

    title: str = Field(..., min_length=2)

    description: Optional[str] = None

    price: float = Field(..., gt=0)

    source_id: int


class ItemPatch(BaseModel):

    title: Optional[str] = None

    description: Optional[str] = None

    price: Optional[float] = None


class ItemResponse(ItemCreate):

    id: int

    class Config:
        from_attributes = True


class SourceCreate(BaseModel):
    name: str
    base_url: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    name: str
    base_url: Optional[str]

    class Config:
        from_attributes = True