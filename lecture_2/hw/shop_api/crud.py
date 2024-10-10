from sqlalchemy.orm import Session
from fastapi import status, HTTPException

from . import models, schemas

from .models import cart_item_association


def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_cart(db: Session, cart_id: int):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()

    if not cart:
        return None

    items_with_quantity = db.query(
        models.Item.id,
        models.Item.name,
        models.Item.deleted,
        cart_item_association.c.quantity
    ).join(cart_item_association,
           models.Item.id == cart_item_association.c.item_id
           ).filter(cart_item_association.c.cart_id == cart_id).all()

    cart_items = []
    for item in items_with_quantity:
        item_info = {
            "id": item.id,
            "name": item.name,
            "quantity": item.quantity,
            "available": not item.deleted
        }
        cart_items.append(item_info)

    cart_data = {
        "id": cart.id,
        "items": cart_items,
        "price": cart.price
    }

    return cart_data


def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, offset: int = 0, limit: int = 10,
              min_price: float = None, max_price: float = None,
              show_deleted: bool = False):
    query = db.query(models.Item)
    if not show_deleted:
        query = query.filter(models.Item.deleted == False)
    if min_price:
        query = query.filter(models.Item.price >= min_price)
    if max_price:
        query = query.filter(models.Item.price <= max_price)
    return query.offset(offset).limit(limit).all()


def get_carts(db: Session, offset: int = 0, limit: int = 10,
              min_price: float = None, max_price: float = None,
              min_quantity: int = None, max_quantity: int = None):
    # Создаем запрос для корзин
    query = db.query(models.Cart)

    if min_price is not None:
        query = query.filter(models.Cart.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Cart.price <= max_price)
    if min_quantity is not None:
        query = query.filter(models.Cart.quantity >= min_quantity)
    if max_quantity is not None:
        query = query.filter(models.Cart.quantity <= max_quantity)

    carts = query.offset(offset).limit(limit).all()

    result = []
    for cart in carts:
        cart_items = []

        # cart_item_alias = aliased(models.Item)

        items_with_quantity = db.query(
            models.Item.id,
            models.Item.name,
            models.Item.deleted,
            cart_item_association.c.quantity
        ).join(cart_item_association,
               models.Item.id == cart_item_association.c.item_id
               ).filter(cart_item_association.c.cart_id == cart.id).all()

        for item in items_with_quantity:
            item_info = {
                "id": item.id,
                "name": item.name,
                "quantity": item.quantity,
                "available": not item.deleted
            }
            cart_items.append(item_info)

        cart_data = {
            "id": cart.id,
            "items": cart_items,
            "price": cart.price
        }
        result.append(cart_data)

    return result


def update_item(db: Session, item_id: int, item: schemas.ItemPut):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        return None
    if item.name is not None:
        db_item.name = item.name
    if item.price is not None:
        db_item.price = item.price
    if hasattr(item, 'deleted') and item.deleted is not None:
        db_item.deleted = item.deleted

    db.commit()
    db.refresh(db_item)

    return db_item


def patch_item(db: Session, item_id: int, item: schemas.ItemBase):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        return None
    if db_item.deleted is True:
        raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED)
    if item.name is not None:
        db_item.name = item.name
    if item.price is not None:
        db_item.price = item.price

    db.commit()
    db.refresh(db_item)

    return db_item


def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None:
        return None
    db_item.deleted = True

    db.commit()
    db.refresh(db_item)

    return db_item


def create_cart(db: Session):
    db_cart = models.Cart()
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart


def item_to_cart(db: Session, cart_id: int, item_id: int, quantity: int = 1):
    db_cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()

    if db_cart is None:
        return None

    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()

    if db_item is None or db_item.deleted:
        return None

    association = db.execute(
        cart_item_association.select().where(
            cart_item_association.c.cart_id == cart_id,
            cart_item_association.c.item_id == item_id
        )
    ).fetchone()

    if association:
        db.execute(
            cart_item_association.update().where(
                cart_item_association.c.cart_id == cart_id,
                cart_item_association.c.item_id == item_id
            ).values(quantity=association[2] + quantity)
        )
    else:
        db.execute(
            cart_item_association.insert().values(
                cart_id=cart_id,
                item_id=item_id,
                quantity=quantity
            )
        )

    db_cart.price += db_item.price * quantity
    db_cart.quantity += quantity

    db.commit()
    db.refresh(db_cart)

    return db_cart
