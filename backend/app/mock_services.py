"""
Mock servisler modülü.
USE_MOCK=true olduğunda gerçek veritabanı yerine kullanılacak mock veriler.
"""

import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from faker import Faker

fake = Faker("tr_TR")  # Türkçe locale


class MockData:
    """Mock veri sınıfı - bellekte tutulan sahte veriler."""

    def __init__(self):
        self.users: List[Dict[str, Any]] = []
        self.orders: List[Dict[str, Any]] = []
        self.stocks: List[Dict[str, Any]] = []
        self._generate_initial_data()

    def _generate_initial_data(self):
        """Başlangıç mock verilerini oluşturur."""
        # Mock kullanıcılar
        for i in range(10):
            user = {
                "id": i + 1,
                "name": fake.name(),
                "email": fake.email(),
                "role": random.choice(["admin", "user", "manager"]),
                "is_active": random.choice([0, 1]),
                "created_at": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
            }
            self.users.append(user)

        # Mock siparişler
        for i in range(20):
            order = {
                "id": i + 1,
                "user_id": random.randint(1, 10),
                "total_amount": round(random.uniform(10.0, 1000.0), 2),
                "status": random.choice(["pending", "completed", "cancelled"]),
                "created_at": fake.date_time_between(
                    start_date="-6m", end_date="now"
                ).isoformat(),
                "order_items": [
                    {
                        "id": i * 10 + j,
                        "product_id": random.randint(1, 50),
                        "quantity": random.randint(1, 5),
                        "unit_price": round(random.uniform(5.0, 200.0), 2),
                        "total_price": 0,  # Hesaplanacak
                    }
                    for j in range(random.randint(1, 3))
                ],
            }
            # Total price hesapla
            for item in order["order_items"]:
                item["total_price"] = item["quantity"] * item["unit_price"]

            self.orders.append(order)

        # Mock stoklar
        for i in range(50):
            stock = {
                "id": i + 1,
                "product_name": fake.company()
                + " "
                + fake.color_name()
                + " "
                + fake.word(),
                "quantity": random.randint(0, 1000),
                "unit_price": round(random.uniform(1.0, 500.0), 2),
                "supplier": fake.company(),
                "created_at": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
            }
            self.stocks.append(stock)


# Global mock data instance
mock_data = MockData()


class MockUserService:
    """Mock kullanıcı servisi."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return mock_data.users

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        return next((user for user in mock_data.users if user["id"] == user_id), None)

    @staticmethod
    def create(user_data: Dict[str, Any]) -> Dict[str, Any]:
        new_user = {
            "id": len(mock_data.users) + 1,
            "name": user_data["name"],
            "email": user_data["email"],
            "role": user_data.get("role", "user"),
            "is_active": int(user_data.get("is_active", True)),
            "created_at": datetime.now().isoformat(),
        }
        mock_data.users.append(new_user)
        return new_user

    @staticmethod
    def update(user_id: int, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        user = MockUserService.get_by_id(user_id)
        if user:
            user.update(user_data)
            return user
        return None

    @staticmethod
    def delete(user_id: int) -> bool:
        user = MockUserService.get_by_id(user_id)
        if user:
            mock_data.users.remove(user)
            return True
        return False


class MockOrderService:
    """Mock sipariş servisi."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return mock_data.orders

    @staticmethod
    def get_by_id(order_id: int) -> Optional[Dict[str, Any]]:
        return next(
            (order for order in mock_data.orders if order["id"] == order_id),
            None,
        )

    @staticmethod
    def create(order_data: Dict[str, Any]) -> Dict[str, Any]:
        new_order = {
            "id": len(mock_data.orders) + 1,
            "user_id": order_data["user_id"],
            "total_amount": order_data["total_amount"],
            "status": order_data.get("status", "pending"),
            "created_at": datetime.now().isoformat(),
            "order_items": order_data.get("order_items", []),
        }
        mock_data.orders.append(new_order)
        return new_order

    @staticmethod
    def update(order_id: int, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        order = MockOrderService.get_by_id(order_id)
        if order:
            order.update(order_data)
            return order
        return None

    @staticmethod
    def delete(order_id: int) -> bool:
        order = MockOrderService.get_by_id(order_id)
        if order:
            mock_data.orders.remove(order)
            return True
        return False


class MockStockService:
    """Mock stok servisi."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        return mock_data.stocks

    @staticmethod
    def get_by_id(stock_id: int) -> Optional[Dict[str, Any]]:
        return next(
            (stock for stock in mock_data.stocks if stock["id"] == stock_id),
            None,
        )

    @staticmethod
    def create(stock_data: Dict[str, Any]) -> Dict[str, Any]:
        new_stock = {
            "id": len(mock_data.stocks) + 1,
            "product_name": stock_data["product_name"],
            "quantity": stock_data["quantity"],
            "unit_price": stock_data["unit_price"],
            "supplier": stock_data.get("supplier", "Unknown"),
            "created_at": datetime.now().isoformat(),
        }
        mock_data.stocks.append(new_stock)
        return new_stock

    @staticmethod
    def update(stock_id: int, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        stock = MockStockService.get_by_id(stock_id)
        if stock:
            stock.update(stock_data)
            return stock
        return None

    @staticmethod
    def delete(stock_id: int) -> bool:
        stock = MockStockService.get_by_id(stock_id)
        if stock:
            mock_data.stocks.remove(stock)
            return True
        return False
