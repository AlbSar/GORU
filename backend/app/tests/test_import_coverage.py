"""
Import Coverage Testi
Tüm modül ve klasörlerin test ortamında import edilebildiğini doğrular.
"""

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


class ImportCoverageTester:
    """Modül import coverage test sınıfı."""

    def __init__(self):
        self.app_root = Path(__file__).parent.parent
        self.import_errors: List[Dict[str, Any]] = []
        self.successful_imports: List[str] = []

    def get_all_python_files(self) -> List[Path]:
        """App klasöründeki tüm Python dosyalarını bul."""
        python_files = []

        for root, dirs, files in os.walk(self.app_root):
            # Test dosyalarını ve cache dosyalarını hariç tut
            exclude_dirs = ["__pycache__", ".pytest_cache", "tests"]
            if any(exclude in root for exclude in exclude_dirs):
                continue

            for file in files:
                if file.endswith(".py") and not file.startswith("test_"):
                    file_path = Path(root) / file
                    python_files.append(file_path)

        return python_files

    def get_all_modules(self) -> List[str]:
        """Import edilecek tüm modülleri listele."""
        modules = []

        # Ana modüller
        main_modules = [
            "app",
            "app.main",
            "app.auth",
            "app.database",
            "app.models",
            "app.schemas",
            "app.mock_routes",
            "app.mock_services",
            "app.test_db",
        ]

        # Core modülleri
        core_modules = [
            "app.core",
            "app.core.security",
            "app.core.settings",
        ]

        # Routes modülleri
        routes_modules = [
            "app.routes",
            "app.routes.common",
            "app.routes.users",
            "app.routes.stocks",
            "app.routes.orders",
        ]

        # Interfaces modülleri
        interfaces_modules = [
            "app.interfaces",
            "app.interfaces.auth_interface",
            "app.interfaces.database_interface",
            "app.interfaces.settings_interface",
        ]

        # Implementations modülleri
        implementations_modules = [
            "app.implementations",
            "app.implementations.auth_implementation",
        ]

        # Middleware modülleri
        middleware_modules = [
            "app.middleware",
            "app.middleware.header_validation",
            "app.middleware.logging_middleware",
            "app.middleware.rate_limiting",
            "app.middleware.security_headers",
        ]

        # Utils modülleri
        utils_modules = [
            "app.utils",
            "app.utils.anonymizer",
        ]

        # Scripts modülleri
        scripts_modules = [
            "app.scripts",
            "app.scripts.create_tables",
            "app.scripts.generate_dummy_data",
            "app.scripts.migrate_to_postgresql",
            "app.scripts.seed_demo_data",
        ]

        modules.extend(main_modules)
        modules.extend(core_modules)
        modules.extend(routes_modules)
        modules.extend(interfaces_modules)
        modules.extend(implementations_modules)
        modules.extend(middleware_modules)
        modules.extend(utils_modules)
        modules.extend(scripts_modules)

        return modules

    def test_import_module(self, module_name: str) -> bool:
        """Tek bir modülü import etmeyi dene."""
        try:
            # Modülü import et
            module = importlib.import_module(module_name)

            # Modülün yüklendiğini doğrula
            assert module is not None, f"Module {module_name} is None"

            # Modülün __name__ attribute'unu kontrol et
            assert hasattr(
                module, "__name__"
            ), f"Module {module_name} has no __name__ attribute"

            self.successful_imports.append(module_name)
            return True

        except ImportError as e:
            error_info = {
                "module": module_name,
                "error_type": "ImportError",
                "error_message": str(e),
                "details": f"Failed to import {module_name}: {e}",
            }
            self.import_errors.append(error_info)
            return False

        except Exception as e:
            error_info = {
                "module": module_name,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "details": f"Unexpected error importing {module_name}: {e}",
            }
            self.import_errors.append(error_info)
            return False

    def test_all_imports(self) -> Dict[str, Any]:
        """Tüm modülleri import etmeyi dene."""
        modules = self.get_all_modules()

        print(f"\n🔍 Testing import coverage for {len(modules)} modules...")
        print("=" * 60)

        for module_name in modules:
            success = self.test_import_module(module_name)
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {module_name}")

        return {
            "total_modules": len(modules),
            "successful_imports": len(self.successful_imports),
            "failed_imports": len(self.import_errors),
            "success_rate": (
                len(self.successful_imports) / len(modules) * 100 if modules else 0
            ),
            "errors": self.import_errors,
            "successful_modules": self.successful_imports,
        }


# Test fonksiyonları
@pytest.fixture
def import_tester():
    """Import tester fixture."""
    return ImportCoverageTester()


def test_import_coverage(import_tester):
    """Ana import coverage testi."""
    results = import_tester.test_all_imports()

    # Sonuçları yazdır
    print("\n" + "=" * 60)
    print("📊 IMPORT COVERAGE RESULTS")
    print("=" * 60)
    print(f"Total modules tested: {results['total_modules']}")
    print(f"Successful imports: {results['successful_imports']}")
    print(f"Failed imports: {results['failed_imports']}")
    print(f"Success rate: {results['success_rate']:.2f}%")

    # Hataları detaylı göster
    if results["errors"]:
        print("\n❌ IMPORT ERRORS:")
        print("-" * 40)
        for error in results["errors"]:
            print(f"Module: {error['module']}")
            print(f"Error Type: {error['error_type']}")
            print(f"Error Message: {error['error_message']}")
            print(f"Details: {error['details']}")
            print("-" * 40)

    # Başarılı importları listele
    if results["successful_modules"]:
        print("\n✅ SUCCESSFUL IMPORTS:")
        print("-" * 40)
        for module in results["successful_modules"]:
            print(f"✓ {module}")

    # Test sonucunu doğrula
    assert results["failed_imports"] == 0, f"Import errors found: {results['errors']}"
    assert (
        results["success_rate"] == 100.0
    ), f"Import success rate is {results['success_rate']}%, expected 100%"


def test_critical_modules():
    """Kritik modüllerin import edilebilirliğini test et."""
    critical_modules = [
        "app.main",
        "app.auth",
        "app.database",
        "app.models",
        "app.schemas",
        "app.core.settings",
        "app.routes.common",
    ]

    for module_name in critical_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Critical module {module_name} is None"
            print(f"✅ Critical module {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Critical module {module_name} failed to import: {e}")


def test_module_attributes():
    """Önemli modüllerin gerekli attribute'larını kontrol et."""
    module_attributes = {
        "app.main": ["app"],
        "app.auth": ["get_current_user"],
        "app.database": ["get_db"],
        "app.models": ["Base"],
        "app.schemas": ["UserCreate", "UserRead"],
    }

    for module_name, expected_attributes in module_attributes.items():
        try:
            module = importlib.import_module(module_name)
            for attr in expected_attributes:
                assert hasattr(
                    module, attr
                ), f"Module {module_name} missing attribute {attr}"
            print(f"✅ Module {module_name} has all required attributes")
        except Exception as e:
            pytest.fail(f"Module {module_name} attribute check failed: {e}")


def test_route_modules():
    """Route modüllerinin import edilebilirliğini test et."""
    route_modules = [
        "app.routes.users",
        "app.routes.stocks",
        "app.routes.orders",
    ]

    for module_name in route_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Route module {module_name} is None"
            print(f"✅ Route module {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Route module {module_name} failed to import: {e}")


def test_middleware_modules():
    """Middleware modüllerinin import edilebilirliğini test et."""
    middleware_modules = [
        "app.middleware.header_validation",
        "app.middleware.logging_middleware",
        "app.middleware.rate_limiting",
        "app.middleware.security_headers",
    ]

    for module_name in middleware_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Middleware module {module_name} is None"
            print(f"✅ Middleware module {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Middleware module {module_name} failed to import: {e}")


def test_utility_modules():
    """Utility modüllerinin import edilebilirliğini test et."""
    utility_modules = [
        "app.utils.anonymizer",
    ]

    for module_name in utility_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Utility module {module_name} is None"
            print(f"✅ Utility module {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Utility module {module_name} failed to import: {e}")


def test_script_modules():
    """Script modüllerinin import edilebilirliğini test et."""
    script_modules = [
        "app.scripts.create_tables",
        "app.scripts.generate_dummy_data",
        "app.scripts.migrate_to_postgresql",
        "app.scripts.seed_demo_data",
    ]

    for module_name in script_modules:
        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"Script module {module_name} is None"
            print(f"✅ Script module {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Script module {module_name} failed to import: {e}")


if __name__ == "__main__":
    # Standalone çalıştırma için
    tester = ImportCoverageTester()
    results = tester.test_all_imports()

    print("\n🎯 Final Results:")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(
        f"Total: {results['total_modules']}, Success: {results['successful_imports']}, Failed: {results['failed_imports']}"
    )

    if results["failed_imports"] > 0:
        sys.exit(1)
    else:
        print("🎉 All imports successful!")
        sys.exit(0)
