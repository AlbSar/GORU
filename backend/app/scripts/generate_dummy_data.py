"""
Dummy data generator script.
Test ve development için sahte veri oluşturur.
"""

import random
import sys
from pathlib import Path

from app.database import SessionLocal
from app.models import Order, OrderItem, Product, Stock, User
from faker import Faker
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

fake = Faker("tr_TR")


def create_dummy_users(db: Session, count: int = 50):
    """Sahte kullanıcılar oluşturur."""
    print(f"Creating {count} dummy users...")

    users = []
    for i in range(count):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            role=random.choice(["admin", "user", "manager", "viewer"]),
            is_active=random.choice([0, 1]),
            password_hash=fake.password(length=12),  # Sahte hash
        )
        users.append(user)

    db.add_all(users)
    db.commit()
    print(f"✅ {count} users created successfully!")
    return users


def create_dummy_stocks(db: Session, count: int = 100):
    """Sahte stok verileri oluşturur."""
    print(f"Creating {count} dummy stocks...")

    # Türkiye'ye özgü ürün isimleri
    product_categories = [
        "Elektronik",
        "Giyim",
        "Kitap",
        "Ev & Yaşam",
        "Spor",
        "Sağlık",
        "Oyuncak",
        "Bahçe",
        "Otomotiv",
        "Kozmetik",
    ]

    stocks = []
    for i in range(count):
        category = random.choice(product_categories)
        product_name = f"{fake.company()} {category} {fake.color_name()} {fake.word()}"

        stock = Stock(
            product_name=product_name,
            quantity=random.randint(0, 1000),
            unit_price=round(random.uniform(5.0, 2000.0), 2),
            supplier=fake.company(),
        )
        stocks.append(stock)

    db.add_all(stocks)
    db.commit()
    print(f"✅ {count} stocks created successfully!")
    return stocks


def create_dummy_orders(db: Session, users: list, stocks: list, count: int = 200):
    """Sahte sipariş verileri oluşturur."""
    print(f"Creating {count} dummy orders...")

    orders = []
    for i in range(count):
        user = random.choice(users)

        # Order oluştur
        order = Order(
            user_id=user.id,
            total_amount=0,  # Hesaplanacak
            status=random.choice(["pending", "completed", "cancelled", "processing"]),
        )

        # Order items oluştur
        items_count = random.randint(1, 5)
        total_amount = 0

        for j in range(items_count):
            stock = random.choice(stocks)
            quantity = random.randint(1, 10)
            unit_price = stock.unit_price
            total_price = quantity * unit_price
            total_amount += total_price

            order_item = OrderItem(
                order=order,
                product_id=stock.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
            order.order_items.append(order_item)

        order.total_amount = round(total_amount, 2)
        orders.append(order)

    db.add_all(orders)
    db.commit()
    print(f"✅ {count} orders created successfully!")
    return orders


def create_dummy_products(db: Session, count: int = 200):
    """Sahte ürün verileri oluşturur."""
    print(f"Creating {count} dummy products...")

    products = []
    for i in range(count):
        product = Product(
            name=f"{fake.company()} {fake.word()} {fake.color_name()}",
            description=fake.text(max_nb_chars=200),
            price=round(random.uniform(10.0, 5000.0), 2),
            category=random.choice(
                [
                    "Elektronik",
                    "Giyim",
                    "Ev & Bahçe",
                    "Spor",
                    "Kitap",
                    "Sağlık",
                    "Otomotiv",
                    "Kozmetik",
                ]
            ),
            is_active=random.choice([True, False]),
        )
        products.append(product)

    db.add_all(products)
    db.commit()
    print(f"✅ {count} products created successfully!")
    return products


def clean_existing_data(db: Session):
    """Mevcut test verilerini temizler."""
    print("🧹 Cleaning existing dummy data...")

    # Order items önce silinmeli (foreign key)
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(Stock).delete()
    db.query(Product).delete()
    db.query(User).delete()

    db.commit()
    print("✅ Existing data cleaned!")


def generate_all_dummy_data():
    """Tüm sahte verileri oluşturur."""
    print("🚀 Starting dummy data generation...")

    # Veritabanı bağlantısı
    db = SessionLocal()

    try:
        # Mevcut verileri temizle (opsiyonel)
        response = input("Do you want to clean existing data? (y/N): ")
        if response.lower() in ["y", "yes"]:
            clean_existing_data(db)

        # Sahte veriler oluştur
        users = create_dummy_users(db, count=50)
        stocks = create_dummy_stocks(db, count=100)
        products = create_dummy_products(db, count=200)
        orders = create_dummy_orders(db, users, stocks, count=200)

        print("\n🎉 All dummy data generated successfully!")
        print("📊 Summary:")
        print(f"   - Users: {len(users)}")
        print(f"   - Stocks: {len(stocks)}")
        print(f"   - Products: {len(products)}")
        print(f"   - Orders: {len(orders)}")

    except Exception as e:
        print(f"❌ Error generating dummy data: {e}")
        db.rollback()
    finally:
        db.close()


# Test uyumluluğu için alias fonksiyonlar
def generate_users(db: Session, count: int = 50):
    """Test uyumluluğu için alias."""
    return create_dummy_users(db, count)


def generate_stocks(db: Session, count: int = 100):
    """Test uyumluluğu için alias."""
    return create_dummy_stocks(db, count)


def generate_orders(db: Session, users: list, stocks: list, count: int = 200):
    """Test uyumluluğu için alias."""
    return create_dummy_orders(db, users, stocks, count)


def main():
    """Main fonksiyon - test uyumluluğu için."""
    generate_all_dummy_data()


if __name__ == "__main__":
    main()
