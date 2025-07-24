from ..database import SessionLocal, engine, Base
from models import (
    User,
    Address,
    Category,
    Product,
    Order,
    OrderItem,
    Stock,
    StockMovement,
)
import datetime

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        # 1. Kullanıcılar
        user1 = User(
            name="Alice",
            email="alice@example.com",
            password_hash="hash1",
            role="admin",
            is_active=1,
        )
        user2 = User(
            name="Bob",
            email="bob@example.com",
            password_hash="hash2",
            role="customer",
            is_active=1,
        )
        db.add_all([user1, user2])
        db.commit()

        # 2. Adresler
        addr1 = Address(
            user_id=1,
            address_line="123 Main St",
            city="Istanbul",
            country="TR",
            postal_code="34000",
            is_default=1,
        )
        addr2 = Address(
            user_id=2,
            address_line="456 Side St",
            city="Ankara",
            country="TR",
            postal_code="06000",
            is_default=1,
        )
        db.add_all([addr1, addr2])
        db.commit()

        # 3. Kategoriler
        cat1 = Category(name="Elektronik", description="Elektronik ürünler")
        cat2 = Category(name="Kitap", description="Kitap ve dergiler")
        db.add_all([cat1, cat2])
        db.commit()

        # 4. Ürünler
        prod1 = Product(
            name="Laptop",
            sku="SKU12345",
            category_id=1,
            price=15000,
            stock=20,
            description="Güçlü laptop",
            is_active=1,
        )
        prod2 = Product(
            name="Roman",
            sku="SKU54321",
            category_id=2,
            price=120,
            stock=100,
            description="Popüler roman",
            is_active=1,
        )
        db.add_all([prod1, prod2])
        db.commit()

        # 5. Siparişler
        order1 = Order(
            user_id=1,
            status="pending",
            total_amount=15120,
            created_at=datetime.datetime.utcnow(),
            shipping_address_id=1,
        )
        db.add(order1)
        db.commit()

        # 6. Sipariş Kalemleri
        item1 = OrderItem(
            order_id=1, product_id=1, quantity=1, unit_price=15000, total_price=15000
        )
        item2 = OrderItem(
            order_id=1, product_id=2, quantity=1, unit_price=120, total_price=120
        )
        db.add_all([item1, item2])
        db.commit()

        # 7. Stoklar
        stock1 = Stock(product_name="Laptop", quantity=19, location="Depo-1")
        stock2 = Stock(product_name="Roman", quantity=99, location="Depo-2")
        db.add_all([stock1, stock2])
        db.commit()

        # 8. Stok Hareketleri
        sm1 = StockMovement(
            product_id=1,
            movement_type="OUT",
            quantity=1,
            source_location="Depo-1",
            dest_location="Kargo",
            created_at=datetime.datetime.utcnow(),
        )
        sm2 = StockMovement(
            product_id=2,
            movement_type="OUT",
            quantity=1,
            source_location="Depo-2",
            dest_location="Kargo",
            created_at=datetime.datetime.utcnow(),
        )
        db.add_all([sm1, sm2])
        db.commit()

        print("Demo/test verileri başarıyla eklendi.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
