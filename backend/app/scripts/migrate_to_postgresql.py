"""
SQLite'den PostgreSQL'e migration script'i.
Development ortamından production'a geçiş için kullanılır.
"""

import os
import sys

from sqlalchemy import create_engine, text

# Environment'ı production olarak ayarla
os.environ["ENVIRONMENT"] = "production"

from ..database import get_database_url, get_engine
from ..models import Base


def migrate_data():
    """SQLite'den PostgreSQL'e veri migration'ı."""
    print("🔄 SQLite'den PostgreSQL'e migration başlıyor...")

    # SQLite source engine
    sqlite_url = "sqlite:///./dev.db"
    sqlite_engine = create_engine(sqlite_url)

    # PostgreSQL target engine
    pg_url = get_database_url()
    pg_engine = create_engine(pg_url)

    try:
        # PostgreSQL'de tabloları oluştur
        Base.metadata.create_all(bind=pg_engine)
        print("✅ PostgreSQL tabloları oluşturuldu")

        # SQLite'dan veri oku
        with sqlite_engine.connect() as sqlite_conn:
            # Users migration
            users = sqlite_conn.execute(text("SELECT * FROM users")).fetchall()
            print(f"📊 {len(users)} kullanıcı bulundu")

            # Stocks migration
            stocks = sqlite_conn.execute(text("SELECT * FROM stocks")).fetchall()
            print(f"📦 {len(stocks)} stok kaydı bulundu")

            # Orders migration
            orders = sqlite_conn.execute(text("SELECT * FROM orders")).fetchall()
            print(f"📋 {len(orders)} sipariş bulundu")

        # PostgreSQL'e veri yaz
        with pg_engine.connect() as pg_conn:
            # Users'ı migrate et
            for user in users:
                pg_conn.execute(
                    text(
                        """
                    INSERT INTO users (id, name, email, password_hash, role, 
                    is_active, created_at, updated_at)
                    VALUES (:id, :name, :email, :password_hash, :role, 
                    :is_active, :created_at, :updated_at)
                """
                    ),
                    user._asdict(),
                )

            # Stocks'ı migrate et
            for stock in stocks:
                pg_conn.execute(
                    text(
                        """
                    INSERT INTO stocks (id, product_name, quantity, location, 
                    created_at)
                    VALUES (:id, :product_name, :quantity, :location, 
                    :created_at)
                """
                    ),
                    stock._asdict(),
                )

            # Orders'ı migrate et
            for order in orders:
                pg_conn.execute(
                    text(
                        """
                    INSERT INTO orders (id, user_id, status, total_amount, 
                    created_at, shipping_address_id)
                    VALUES (:id, :user_id, :status, :total_amount, 
                    :created_at, :shipping_address_id)
                """
                    ),
                    order._asdict(),
                )

            pg_conn.commit()

        print("✅ Migration başarıyla tamamlandı!")
        print(
            f"📊 Toplam {len(users)} kullanıcı, {len(stocks)} stok, "
            f"{len(orders)} sipariş migrate edildi"
        )

    except Exception as e:
        print(f"❌ Migration hatası: {e}")
        return False

    return True


def verify_migration():
    """Migration'ı doğrula."""
    print("🔍 Migration doğrulaması...")

    pg_engine = get_engine()

    with pg_engine.connect() as conn:
        # Veri sayılarını kontrol et
        user_count = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        stock_count = conn.execute(text("SELECT COUNT(*) FROM stocks")).scalar()
        order_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar()

        print(f"✅ PostgreSQL'de {user_count} kullanıcı")
        print(f"✅ PostgreSQL'de {stock_count} stok")
        print(f"✅ PostgreSQL'de {order_count} sipariş")

        if user_count > 0 and stock_count > 0:
            print("✅ Migration doğrulaması başarılı!")
            return True
        else:
            print("❌ Migration doğrulaması başarısız!")
            return False


if __name__ == "__main__":
    print("🚀 SQLite'den PostgreSQL'e Migration Tool")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_migration()
    else:
        success = migrate_data()
        if success:
            verify_migration()
        else:
            print("❌ Migration başarısız!")
            sys.exit(1)
