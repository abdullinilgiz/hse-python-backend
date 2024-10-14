from sqlalchemy import (Boolean,
                        Column,
                        ForeignKey,
                        Integer,
                        String,
                        Float,
                        Table, )
from sqlalchemy.orm import relationship

from database import Base


cart_item_association = Table(
    'cart_item_association',
    Base.metadata,
    Column('cart_id', Integer, ForeignKey('carts.id')),
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('quantity', Integer),
)


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    price = Column(Float)
    deleted = Column(Boolean, default=False)

    carts = relationship("Cart", secondary=cart_item_association,
                         back_populates="items")


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    price = Column(Float, default=0)
    items = relationship("Item", secondary=cart_item_association,
                         back_populates="carts")
    quantity = Column(Integer, default=0)
