"""
Stok endpoint'leri.
ERP sistemi için stok yönetimi CRUD işlemlerini sağlar.
"""

from typing import List

from app.auth import get_current_user
from app.models import Stock
from app.routes.common import get_db
from app.schemas import StockCreate, StockRead, StockUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/",
    response_model=StockRead,
    status_code=status.HTTP_201_CREATED,
    summary="Stok ekle / Create stock",
    responses={
        201: {"description": "Stok başarıyla eklendi / Stock created."},
        400: {
            "description": "Benzersiz ürün adı veya geçersiz veri / "
            "Unique product name or invalid data."
        },
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
def create_stock(
    stock: StockCreate,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Yeni stok kaydı ekler. Ürün adı benzersiz olmalıdır.
    EN: Creates a new stock record. Product name must be unique.
    """
    if db.query(Stock).filter(Stock.product_name == stock.product_name).first():
        raise HTTPException(
            status_code=400,
            detail="Product name already exists",
        )
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


@router.get(
    "/",
    response_model=List[StockRead],
    summary="Stokları listele / List stocks",
    responses={
        200: {"description": "Stok listesi / List of stocks."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
def list_stocks(db: Session = Depends(get_db), user_auth=Depends(get_current_user)):
    """
    TR: Tüm stokları listeler.
    EN: Lists all stocks.
    """
    return db.query(Stock).all()


@router.get(
    "/{id}",
    response_model=StockRead,
    summary="Stok detay / Stock detail",
    responses={
        200: {"description": "Stok detayı / Stock detail."},
        404: {"description": "Stok bulunamadı / Stock not found."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
def get_stock(
    id: int, db: Session = Depends(get_db), user_auth=Depends(get_current_user)
):
    """
    TR: Tek stok kaydını getirir.
    EN: Returns a single stock record.
    """
    stock = db.query(Stock).filter(Stock.id == id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stok bulunamadı / Stock not found")
    return stock


@router.put(
    "/{id}",
    response_model=StockRead,
    summary="Stok güncelle / Update stock",
    responses={
        200: {"description": "Stok güncellendi / Stock updated."},
        404: {"description": "Stok bulunamadı / Stock not found."},
        400: {
            "description": "Benzersiz ürün adı veya geçersiz veri / "
            "Unique product name or invalid data."
        },
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
def update_stock(
    id: int,
    stock: StockUpdate,
    db: Session = Depends(get_db),
    user_auth=Depends(get_current_user),
):
    """
    TR: Stok kaydını günceller.
    EN: Updates a stock record.
    """
    db_stock = db.query(Stock).filter(Stock.id == id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stok bulunamadı / Stock not found")
    if (
        stock.product_name
        and db.query(Stock)
        .filter(Stock.product_name == stock.product_name, Stock.id != id)
        .first()
    ):
        raise HTTPException(
            status_code=400,
            detail="Product name already exists",
        )
    for key, value in stock.model_dump(exclude_unset=True).items():
        setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return db_stock


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Stok sil / Delete stock",
    responses={
        204: {"description": "Stok silindi / Stock deleted."},
        404: {"description": "Stok bulunamadı / Stock not found."},
        401: {"description": "Yetkisiz / Unauthorized"},
    },
)
def delete_stock(
    id: int, db: Session = Depends(get_db), user_auth=Depends(get_current_user)
):
    """
    TR: Stok kaydını siler.
    EN: Deletes a stock record.
    """
    db_stock = db.query(Stock).filter(Stock.id == id).first()
    if not db_stock:
        raise HTTPException(status_code=404, detail="Stok bulunamadı / Stock not found")
    db.delete(db_stock)
    db.commit()
    return
