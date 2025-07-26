"""
Mock API endpoint'leri.
USE_MOCK=true olduğunda kullanılacak sahte API endpoint'leri.

Bu modül sadece USE_MOCK environment variable true olduğunda aktif olur.
Mock endpoint'ler gerçek veritabanı yerine in-memory data kullanır.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, status

from .core.settings import settings
from .mock_services import MockOrderService, MockStockService, MockUserService

# Mock router sadece USE_MOCK=true ise etkinleşir
mock_router = APIRouter(
    prefix=settings.MOCK_API_PREFIX,
    tags=["Mock API"],
    responses={
        404: {"description": "Mock resource not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)


# ============================================================================
# MOCK USERS ENDPOINTS
# ============================================================================


@mock_router.get(
    "/users",
    response_model=List[Dict[str, Any]],
    summary="Mock kullanıcı listesini getir",
    description="Tüm mock kullanıcıları listeler. Gerçek veritabanı yerine in-memory data kullanır.",
)
async def get_mock_users(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(
        100, ge=1, le=1000, description="Döndürülecek maksimum kayıt sayısı"
    ),
):
    """Mock kullanıcı listesini döner."""
    users = MockUserService.get_all()
    return users[skip : skip + limit]


@mock_router.get(
    "/users/{user_id}",
    response_model=Dict[str, Any],
    summary="ID'ye göre mock kullanıcı getir",
    description="Belirtilen ID'ye sahip mock kullanıcıyı döner.",
)
async def get_mock_user(user_id: int = Path(..., gt=0, description="Kullanıcı ID'si")):
    """ID'ye göre mock kullanıcı döner."""
    user = MockUserService.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@mock_router.post(
    "/users",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Yeni mock kullanıcı oluştur",
    description="Yeni bir mock kullanıcı oluşturur ve döner.",
)
async def create_mock_user(user_data: Dict[str, Any]):
    """Yeni mock kullanıcı oluşturur."""
    return MockUserService.create(user_data)


@mock_router.put(
    "/users/{user_id}",
    response_model=Dict[str, Any],
    summary="Mock kullanıcı güncelle",
    description="Belirtilen ID'ye sahip mock kullanıcıyı günceller.",
)
async def update_mock_user(
    user_id: int = Path(..., gt=0, description="Kullanıcı ID'si"),
    user_data: Dict[str, Any] = None,
):
    """Mock kullanıcı günceller."""
    user = MockUserService.update(user_id, user_data or {})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


@mock_router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mock kullanıcı sil",
    description="Belirtilen ID'ye sahip mock kullanıcıyı siler.",
)
async def delete_mock_user(
    user_id: int = Path(..., gt=0, description="Kullanıcı ID'si")
):
    """Mock kullanıcı siler."""
    success = MockUserService.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )


# ============================================================================
# MOCK ORDERS ENDPOINTS
# ============================================================================


@mock_router.get(
    "/orders",
    response_model=List[Dict[str, Any]],
    summary="Mock sipariş listesini getir",
    description="Tüm mock siparişleri listeler.",
)
async def get_mock_orders(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(
        100, ge=1, le=1000, description="Döndürülecek maksimum kayıt sayısı"
    ),
):
    """Mock sipariş listesini döner."""
    orders = MockOrderService.get_all()
    return orders[skip : skip + limit]


@mock_router.get(
    "/orders/{order_id}",
    response_model=Dict[str, Any],
    summary="ID'ye göre mock sipariş getir",
    description="Belirtilen ID'ye sahip mock siparişi döner.",
)
async def get_mock_order(order_id: int = Path(..., gt=0, description="Sipariş ID'si")):
    """ID'ye göre mock sipariş döner."""
    order = MockOrderService.get_by_id(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    return order


@mock_router.post(
    "/orders",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Yeni mock sipariş oluştur",
    description="Yeni bir mock sipariş oluşturur ve döner.",
)
async def create_mock_order(order_data: Dict[str, Any]):
    """Yeni mock sipariş oluşturur."""
    return MockOrderService.create(order_data)


@mock_router.put(
    "/orders/{order_id}",
    response_model=Dict[str, Any],
    summary="Mock sipariş güncelle",
    description="Belirtilen ID'ye sahip mock siparişi günceller.",
)
async def update_mock_order(
    order_id: int = Path(..., gt=0, description="Sipariş ID'si"),
    order_data: Dict[str, Any] = None,
):
    """Mock sipariş günceller."""
    order = MockOrderService.update(order_id, order_data or {})
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )
    return order


@mock_router.delete(
    "/orders/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mock sipariş sil",
    description="Belirtilen ID'ye sahip mock siparişi siler.",
)
async def delete_mock_order(
    order_id: int = Path(..., gt=0, description="Sipariş ID'si")
):
    """Mock sipariş siler."""
    success = MockOrderService.delete(order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found",
        )


# ============================================================================
# MOCK STOCKS ENDPOINTS
# ============================================================================


@mock_router.get(
    "/stocks",
    response_model=List[Dict[str, Any]],
    summary="Mock stok listesini getir",
    description="Tüm mock stokları listeler.",
)
async def get_mock_stocks(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(
        100, ge=1, le=1000, description="Döndürülecek maksimum kayıt sayısı"
    ),
):
    """Mock stok listesini döner."""
    stocks = MockStockService.get_all()
    return stocks[skip : skip + limit]


@mock_router.get(
    "/stocks/{stock_id}",
    response_model=Dict[str, Any],
    summary="ID'ye göre mock stok getir",
    description="Belirtilen ID'ye sahip mock stoku döner.",
)
async def get_mock_stock(stock_id: int = Path(..., gt=0, description="Stok ID'si")):
    """ID'ye göre mock stok döner."""
    stock = MockStockService.get_by_id(stock_id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with id {stock_id} not found",
        )
    return stock


@mock_router.post(
    "/stocks",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Yeni mock stok oluştur",
    description="Yeni bir mock stok oluşturur ve döner.",
)
async def create_mock_stock(stock_data: Dict[str, Any]):
    """Yeni mock stok oluşturur."""
    return MockStockService.create(stock_data)


@mock_router.put(
    "/stocks/{stock_id}",
    response_model=Dict[str, Any],
    summary="Mock stok güncelle",
    description="Belirtilen ID'ye sahip mock stoku günceller.",
)
async def update_mock_stock(
    stock_id: int = Path(..., gt=0, description="Stok ID'si"),
    stock_data: Dict[str, Any] = None,
):
    """Mock stok günceller."""
    stock = MockStockService.update(stock_id, stock_data or {})
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with id {stock_id} not found",
        )
    return stock


@mock_router.delete(
    "/stocks/{stock_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mock stok sil",
    description="Belirtilen ID'ye sahip mock stoku siler.",
)
async def delete_mock_stock(stock_id: int = Path(..., gt=0, description="Stok ID'si")):
    """Mock stok siler."""
    success = MockStockService.delete(stock_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with id {stock_id} not found",
        )
