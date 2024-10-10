from pydantic import BaseModel
from typing import List, Optional


class ItemBase(BaseModel):
    name: str
    price: float


class ItemCreate(ItemBase):
    pass


class ItemPatch(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

    class Config:
        extra = "forbid"


class ItemPut(ItemBase):
    deleted: bool = False


class Item(ItemBase):
    id: int
    deleted: bool = False

    class Config:
        from_attributes = True


class CartBase(BaseModel):
    pass


class Cart(CartBase):
    id: int
    items: List[Item] = []
    price: float

    class Config:
        from_attributes = True


class ItemInCart(BaseModel):
    id: int
    name: str
    quantity: int
    available: bool


class CartList(CartBase):
    id: int
    items: List[ItemInCart] = []
    price: float

    class Config:
        from_attributes = True
