from typing import List

from fastapi import Depends, FastAPI, HTTPException, status, Response
from sqlalchemy.orm import Session

from prometheus_fastapi_instrumentator import Instrumentator

import crud
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
Instrumentator().instrument(app).expose(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/item", response_model=schemas.Item,
          status_code=status.HTTP_201_CREATED)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    item = crud.create_item(db, item)
    return item


@app.get("/item/{item_id}", response_model=schemas.Item)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.get_item(db, item_id)
    if item is None or item.deleted is True:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item


@app.get("/item", response_model=List[schemas.Item])
def get_items(offset: int = 0, limit: int = 10,
              min_price: float = None, max_price: float = None,
              show_deleted: bool = False, db: Session = Depends(get_db)):
    if offset is not None and offset < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if limit is not None and limit < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    items = crud.get_items(db, offset, limit,
                           min_price, max_price, show_deleted)
    return items


@app.put("/item/{item_id}", response_model=schemas.Item)
def put_item(item_id: int, item: schemas.ItemPut,
             db: Session = Depends(get_db)):
    item = crud.update_item(db=db, item_id=item_id, item=item)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item


@app.patch("/item/{item_id}", response_model=schemas.Item)
def patch_item(item_id: int, item: schemas.ItemPatch,
               db: Session = Depends(get_db)):
    item = crud.patch_item(db=db, item_id=item_id, item=item)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item


@app.delete("/item/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return item


@app.post("/cart", response_model=schemas.Cart,
          status_code=status.HTTP_201_CREATED)
def create_cart(response: Response, db: Session = Depends(get_db)):
    cart = crud.create_cart(db=db)
    response.headers["Location"] = f"/cart/{cart.id}"
    return cart


@app.get("/cart/{item_id}", response_model=schemas.CartList)
def get_cart(item_id: int, db: Session = Depends(get_db)):
    cart = crud.get_cart(db, item_id)
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return cart


@app.post("/cart/{cart_id}/add/{item_id}", response_model=schemas.Cart)
def add_item_to_cart(cart_id: int, item_id: int,
                     db: Session = Depends(get_db)):
    if crud.get_item(db=db, item_id=item_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if crud.get_cart(db=db, cart_id=cart_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    cart = crud.item_to_cart(db, cart_id, item_id)
    if cart is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return cart


@app.get("/cart", response_model=List[schemas.CartList])
def get_carts(offset: int = 0, limit: int = 10,
              min_price: float = None, max_price: float = None,
              min_quantity: int = None, max_quantity: int = None,
              db: Session = Depends(get_db)):
    if offset is not None and offset < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if limit is not None and limit < 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if min_price is not None and min_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if max_price is not None and max_price < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if min_quantity is not None and min_quantity < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if max_quantity is not None and max_quantity < 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
    carts = crud.get_carts(db, offset, limit,
                           min_price, max_price,
                           min_quantity, max_quantity)
    return carts
