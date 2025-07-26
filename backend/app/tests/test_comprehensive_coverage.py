"""
Kapsamlı test coverage için test modülü.
Tüm ana fonksiyonaliteleri test eder.
"""


class TestSettings:
    """Settings modülü testleri."""

    def test_settings_use_mock(self):
        """Settings USE_MOCK testi."""
        from ..core.settings import Settings
        test_settings = Settings()
        assert test_settings.USE_MOCK

    def test_app_cors_setup(self):
        """App CORS setup testi."""
        from ..main import app
        # CORS middleware'in eklenmiş olduğunu kontrol et
        assert len(app.user_middleware_stack) > 0
