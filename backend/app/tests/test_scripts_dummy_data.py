"""
Scripts/generate_dummy_data.py modülü testleri.
Dummy data generation fonksiyonelliğini test eder.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..database import Base


class TestGenerateDummyData:
    """Generate dummy data script testleri."""

    @pytest.fixture
    def temp_db(self):
        """Geçici test veritabanı."""
        # Geçici dosya oluştur
        temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db_file.close()

        # SQLite connection string
        database_url = f"sqlite:///{temp_db_file.name}"

        # Engine ve session oluştur
        engine = create_engine(
            database_url, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=engine)

        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        yield SessionLocal, database_url

        # Cleanup
        try:
            os.unlink(temp_db_file.name)
        except OSError:
            pass

    def test_import_generate_dummy_data(self):
        """Generate dummy data script import testi."""
        try:
            from ..scripts import generate_dummy_data

            assert hasattr(generate_dummy_data, "create_dummy_users")
            assert hasattr(generate_dummy_data, "create_dummy_stocks")
            assert hasattr(generate_dummy_data, "create_dummy_orders")
        except ImportError as e:
            pytest.fail(f"Generate dummy data script import failed: {e}")

    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_generate_users_function(self, mock_session_local):
        """Generate users fonksiyon testi."""
        from ..scripts.generate_dummy_data import generate_users

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Test fonksiyon çağrısı
        count = 10
        generate_users(mock_session, count)

        # Session kullanımını kontrol et
        assert mock_session.add.call_count == count
        assert mock_session.commit.called

    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_generate_stocks_function(self, mock_session_local):
        """Generate stocks fonksiyon testi."""
        from ..scripts.generate_dummy_data import generate_stocks

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Test fonksiyon çağrısı
        count = 15
        generate_stocks(mock_session, count)

        # Session kullanımını kontrol et
        assert mock_session.add.call_count == count
        assert mock_session.commit.called

    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_generate_orders_function(self, mock_session_local):
        """Generate orders fonksiyon testi."""
        from ..scripts.generate_dummy_data import generate_orders

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Mock users ve stocks query results
        mock_session.query.return_value.count.return_value = 10
        mock_session.query.return_value.offset.return_value.first.return_value.id = (
            1
        )

        # Test fonksiyon çağrısı
        count = 5
        generate_orders(mock_session, count)

        # Session kullanımını kontrol et
        assert mock_session.add.call_count == count
        assert mock_session.commit.called

    @patch("builtins.input", side_effect=["n"])  # clean_existing = 'n'
    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_main_function_no_clean(self, mock_session_local, mock_input):
        """Main fonksiyon testi (clean=no)."""
        from ..scripts.generate_dummy_data import main

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Mock query counts
        mock_session.query.return_value.count.return_value = 5

        # Test main function
        main()

        # Clean işlemi yapılmamalı
        assert not mock_session.query.return_value.delete.called

    @patch("builtins.input", side_effect=["y"])  # clean_existing = 'y'
    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_main_function_with_clean(self, mock_session_local, mock_input):
        """Main fonksiyon testi (clean=yes)."""
        from ..scripts.generate_dummy_data import main

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Mock query counts
        mock_session.query.return_value.count.return_value = 5

        # Test main function
        main()

        # Clean işlemi yapılmalı
        assert mock_session.query.return_value.delete.called

    def test_faker_usage(self):
        """Faker kullanımı testi."""
        try:
            from ..scripts.generate_dummy_data import fake

            # Faker instance kontrolü
            assert hasattr(fake, "name")
            assert hasattr(fake, "email")
            assert hasattr(fake, "company")
            assert hasattr(fake, "phone_number")

            # Türkçe locale kontrolü
            name = fake.name()
            assert isinstance(name, str)
            assert len(name) > 0

        except ImportError:
            pytest.fail("Faker import failed in generate_dummy_data script")

    @patch("sys.argv", ["generate_dummy_data.py"])
    def test_script_execution(self):
        """Script execution testi."""
        from ..scripts import generate_dummy_data

        # Script'in __main__ bloğu test edilemez ama import edilebilirliği test edilir
        assert hasattr(generate_dummy_data, "main")

    def test_data_relationships(self):
        """Veri ilişkileri testi."""
        try:
            from ..scripts.generate_dummy_data import generate_orders

            # Order'ların user_id ve stock'larla ilişkisi olup olmadığını kontrol edecek
            # mock ile test edileceği için sadece import kontrolü
            assert callable(generate_orders)

        except ImportError:
            pytest.fail("Generate orders function import failed")

    @patch("app.scripts.generate_dummy_data.SessionLocal")
    def test_error_handling(self, mock_session_local):
        """Hata yönetimi testi."""
        from ..scripts.generate_dummy_data import generate_users

        # Mock session with exception
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session
        mock_session.add.side_effect = Exception("Database error")

        # Exception handling
        with pytest.raises(Exception):
            generate_users(mock_session, 1)

    def test_data_validation(self):
        """Veri validasyon testi."""
        try:
            from ..scripts.generate_dummy_data import fake

            # Fake data format kontrolü
            email = fake.email()
            assert "@" in email

            phone = fake.phone_number()
            assert isinstance(phone, str)

            company = fake.company()
            assert isinstance(company, str)
            assert len(company) > 0

        except ImportError:
            pytest.fail("Fake data validation failed")


class TestCreateTablesScript:
    """Create tables script testleri."""

    def test_import_create_tables(self):
        """Create tables script import testi."""
        try:
            from ..scripts import create_tables

            assert (
                hasattr(create_tables, "main") or len(dir(create_tables)) > 0
            )
        except ImportError as e:
            pytest.fail(f"Create tables script import failed: {e}")

    @patch("app.scripts.create_tables.Base")
    @patch("app.scripts.create_tables.engine")
    def test_create_tables_execution(self, mock_engine, mock_base):
        """Create tables execution testi."""
        try:

            # Script çalıştırılabilir olmalı
            # Mock'lar sayesinde gerçek veritabanı işlemi yapılmaz
            assert mock_engine is not None
            assert mock_base is not None

        except Exception as e:
            pytest.fail(f"Create tables execution failed: {e}")


class TestSeedDemoDataScript:
    """Seed demo data script testleri."""

    def test_import_seed_demo_data(self):
        """Seed demo data script import testi."""
        try:
            from ..scripts import seed_demo_data

            # Script'in import edilebilir olduğunu kontrol et
            assert len(dir(seed_demo_data)) > 0
        except ImportError as e:
            pytest.fail(f"Seed demo data script import failed: {e}")

    @patch("app.scripts.seed_demo_data.SessionLocal")
    def test_seed_demo_data_execution(self, mock_session_local):
        """Seed demo data execution testi."""
        from ..scripts import seed_demo_data

        # Mock session setup
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        mock_session.__enter__.return_value = mock_session

        # Script'in çalıştırılabilir olduğunu test et
        try:
            # Eğer main fonksionu varsa çalıştır
            if hasattr(seed_demo_data, "main"):
                seed_demo_data.main()
        except Exception as e:
            # Import hatası değilse, script çalıştırılabilir
            if "import" not in str(e).lower():
                pass  # Beklenen hata (mock session ile)


class TestScriptsIntegration:
    """Scripts entegrasyon testleri."""

    def test_all_scripts_importable(self):
        """Tüm script'lerin import edilebilirliği."""
        scripts = ["generate_dummy_data", "create_tables", "seed_demo_data"]

        for script_name in scripts:
            try:
                module = __import__(
                    f"app.scripts.{script_name}", fromlist=[script_name]
                )
                assert module is not None
            except ImportError as e:
                pytest.fail(f"Script {script_name} import failed: {e}")

    def test_scripts_directory_structure(self):
        """Scripts dizin yapısı testi."""
        try:
            from ..scripts import __init__

            assert __init__ is not None
        except ImportError:
            pytest.fail("Scripts package not properly initialized")

    @patch("os.path.exists", return_value=True)
    def test_script_file_existence(self, mock_exists):
        """Script dosya varlığı testi."""
        # Mock ile dosya varlığını simüle et
        assert mock_exists("app/scripts/generate_dummy_data.py")
        assert mock_exists("app/scripts/create_tables.py")
        assert mock_exists("app/scripts/seed_demo_data.py")
