"""
Test configuration and settings
"""
import os
import pytest
from app.core.config import Settings


class TestCORSConfiguration:
    """Test CORS origins configuration and validator"""
    
    def test_default_cors_origins(self):
        """Test default CORS origins are List[str]"""
        settings = Settings()
        assert isinstance(settings.BACKEND_CORS_ORIGINS, list)
        assert all(isinstance(origin, str) for origin in settings.BACKEND_CORS_ORIGINS)
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
        assert "http://frontend:3000" in settings.BACKEND_CORS_ORIGINS
        assert "http://127.0.0.1:3000" in settings.BACKEND_CORS_ORIGINS
    
    def test_cors_origins_from_comma_separated_env(self):
        """Test CORS origins from comma-separated environment variable"""
        # Note: Environment variables need to be set before Settings instantiation
        import os
        original = os.environ.get("BACKEND_CORS_ORIGINS")
        try:
            os.environ["BACKEND_CORS_ORIGINS"] = "http://example.com,http://test.com,http://app.com"
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 3
            assert "http://example.com" in settings.BACKEND_CORS_ORIGINS
            assert "http://test.com" in settings.BACKEND_CORS_ORIGINS
            assert "http://app.com" in settings.BACKEND_CORS_ORIGINS
        finally:
            if original:
                os.environ["BACKEND_CORS_ORIGINS"] = original
            else:
                os.environ.pop("BACKEND_CORS_ORIGINS", None)
    
    def test_cors_origins_from_json_env(self):
        """Test CORS origins from JSON environment variable"""
        import os
        original = os.environ.get("BACKEND_CORS_ORIGINS")
        try:
            os.environ["BACKEND_CORS_ORIGINS"] = '["http://json1.com","http://json2.com"]'
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 2
            assert "http://json1.com" in settings.BACKEND_CORS_ORIGINS
            assert "http://json2.com" in settings.BACKEND_CORS_ORIGINS
        finally:
            if original:
                os.environ["BACKEND_CORS_ORIGINS"] = original
            else:
                os.environ.pop("BACKEND_CORS_ORIGINS", None)
    
    def test_cors_origins_with_whitespace(self):
        """Test CORS origins with whitespace in comma-separated string"""
        import os
        original = os.environ.get("BACKEND_CORS_ORIGINS")
        try:
            os.environ["BACKEND_CORS_ORIGINS"] = "http://a.com , http://b.com , http://c.com"
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 3
            assert "http://a.com" in settings.BACKEND_CORS_ORIGINS
            assert "http://b.com" in settings.BACKEND_CORS_ORIGINS
            assert "http://c.com" in settings.BACKEND_CORS_ORIGINS
        finally:
            if original:
                os.environ["BACKEND_CORS_ORIGINS"] = original
            else:
                os.environ.pop("BACKEND_CORS_ORIGINS", None)
    
    def test_cors_origins_type_is_list_str(self):
        """Test that CORS origins type is List[str] not List[AnyHttpUrl]"""
        settings = Settings()
        # This should work with any string, not just valid URLs
        settings.BACKEND_CORS_ORIGINS = ["http://valid.com", "custom-origin", "localhost:3000"]
        assert len(settings.BACKEND_CORS_ORIGINS) == 3


class TestDatabaseConfiguration:
    """Test database configuration"""
    
    def test_async_database_url_conversion(self):
        """Test PostgreSQL URL is converted to async URL"""
        settings = Settings()
        settings.DATABASE_URL = "postgresql://user:pass@localhost/db"
        assert settings.ASYNC_DATABASE_URL == "postgresql+asyncpg://user:pass@localhost/db"
    
    def test_async_database_url_no_conversion(self):
        """Test non-PostgreSQL URL is not converted"""
        settings = Settings()
        settings.DATABASE_URL = "sqlite:///test.db"
        assert settings.ASYNC_DATABASE_URL == "sqlite:///test.db"


class TestSecuritySettings:
    """Test security configuration"""
    
    def test_secret_key_generation(self):
        """Test SECRET_KEY is generated if not set"""
        settings = Settings()
        assert settings.SECRET_KEY
        assert len(settings.SECRET_KEY) > 20
    
    def test_secret_key_from_env(self):
        """Test SECRET_KEY from environment variable"""
        import os
        original = os.environ.get("SECRET_KEY")
        try:
            test_key = "test-secret-key-12345"
            os.environ["SECRET_KEY"] = test_key
            settings = Settings()
            assert settings.SECRET_KEY == test_key
        finally:
            if original:
                os.environ["SECRET_KEY"] = original
            else:
                os.environ.pop("SECRET_KEY", None)
    
    def test_token_expiry_settings(self):
        """Test token expiry settings have default values"""
        settings = Settings()
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS == 24