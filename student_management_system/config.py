"""
Configuration management system for the Student Management System.

This module provides a centralized configuration system with:
- Environment variable validation
- Error handling for missing configurations
- Fallback mechanisms
- Configuration documentation
- Configuration versioning
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Type, Union
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from dotenv import load_dotenv
import logging
from functools import lru_cache
from django.core.exceptions import ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration version for tracking changes
CONFIG_VERSION = "1.0.0"


def parse_optional_int(value: Any) -> Optional[int]:
    """Parse a value into an optional integer."""
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    engine: str = Field(default="django.db.backends.sqlite3")
    name: str = Field(default="db.sqlite3")
    timeout: int = Field(default=20)
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_optional_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "port" in values:
            values["port"] = parse_optional_int(values["port"])
        return values


class CacheConfig(BaseModel):
    """Cache configuration settings."""

    use_redis: bool = Field(default=False)
    redis_url: str = Field(default="redis://localhost:6379/1")
    timeout: int = Field(default=300)
    key_prefix: str = Field(default="sms")
    max_connections: int = Field(default=1000)


class EmailConfig(BaseModel):
    """Email configuration settings."""

    backend: str = Field(default="django.core.mail.backends.console.EmailBackend")
    default_from_email: str = Field(default="noreply@studentmanagementsystem.com")
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = Field(default=True)

    @model_validator(mode="before")
    @classmethod
    def validate_optional_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if "port" in values:
            values["port"] = parse_optional_int(values["port"])
        return values


class FirebaseConfig(BaseModel):
    """Firebase configuration settings."""

    api_key: str
    auth_domain: str
    project_id: str
    storage_bucket: str
    messaging_sender_id: str
    app_id: str
    measurement_id: str


class SMSConfig(BaseModel):
    """SMS configuration settings."""

    api_key: str
    sender_id: str = Field(default="SMSSYS")


class GunicornConfig(BaseModel):
    """Gunicorn configuration settings."""

    workers: int = Field(default=4)
    threads: int = Field(default=2)
    timeout: int = Field(default=30)
    keepalive: int = Field(default=2)


class Config(BaseModel):
    """Main configuration model."""

    version: str = Field(default=CONFIG_VERSION)
    debug: bool = Field(default=False)
    secret_key: str
    allowed_hosts: list[str] = Field(default=["*"])
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    firebase: FirebaseConfig
    sms: SMSConfig
    gunicorn: GunicornConfig = Field(default_factory=GunicornConfig)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_config() -> Config:
    """
    Get the application configuration.

    Returns:
        Config: The validated configuration object.

    Raises:
        ValidationError: If required environment variables are missing or invalid.
    """
    # Load environment variables
    load_dotenv()

    try:
        config = Config(
            debug=os.getenv("DJANGO_DEBUG", "False").lower() == "true",
            secret_key=os.getenv("DJANGO_SECRET_KEY", ""),
            allowed_hosts=os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(","),
            database=DatabaseConfig(
                engine=os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
                name=os.getenv("DB_NAME", "db.sqlite3"),
                timeout=int(os.getenv("DB_TIMEOUT", "20")),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
            ),
            cache=CacheConfig(
                use_redis=os.getenv("USE_REDIS_CACHE", "False").lower() == "true",
                redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/1"),
                timeout=int(os.getenv("CACHE_TIMEOUT", "300")),
                key_prefix=os.getenv("CACHE_KEY_PREFIX", "sms"),
                max_connections=int(os.getenv("CACHE_MAX_CONNECTIONS", "1000")),
            ),
            email=EmailConfig(
                backend=os.getenv(
                    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
                ),
                default_from_email=os.getenv(
                    "DEFAULT_FROM_EMAIL", "noreply@studentmanagementsystem.com"
                ),
                host=os.getenv("EMAIL_HOST"),
                port=os.getenv("EMAIL_PORT"),
                username=os.getenv("EMAIL_USERNAME"),
                password=os.getenv("EMAIL_PASSWORD"),
                use_tls=os.getenv("EMAIL_USE_TLS", "True").lower() == "true",
            ),
            firebase=FirebaseConfig(
                api_key=os.getenv("FIREBASE_API_KEY", ""),
                auth_domain=os.getenv("FIREBASE_AUTH_DOMAIN", ""),
                project_id=os.getenv("FIREBASE_PROJECT_ID", ""),
                storage_bucket=os.getenv("FIREBASE_STORAGE_BUCKET", ""),
                messaging_sender_id=os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
                app_id=os.getenv("FIREBASE_APP_ID", ""),
                measurement_id=os.getenv("FIREBASE_MEASUREMENT_ID", ""),
            ),
            sms=SMSConfig(
                api_key=os.getenv("SMS_API_KEY", ""),
                sender_id=os.getenv("SMS_SENDER_ID", "SMSSYS"),
            ),
            gunicorn=GunicornConfig(
                workers=int(os.getenv("GUNICORN_WORKERS", "4")),
                threads=int(os.getenv("GUNICORN_THREADS", "2")),
                timeout=int(os.getenv("GUNICORN_TIMEOUT", "30")),
                keepalive=int(os.getenv("GUNICORN_KEEPALIVE", "2")),
            ),
        )

        # Validate required fields
        if not config.secret_key:
            # Check if running tests and provide fallback for testing
            import sys

            if "test" in sys.argv:
                config.secret_key = "django-insecure-test-key-only-for-testing"
            else:
                from django.core.exceptions import ValidationError

                raise ValidationError(f"DJANGO_SECRET_KEY is required")

        if not config.firebase.api_key:
            # Check if running tests
            import sys

            if "test" in sys.argv:
                config.firebase.api_key = "test-firebase-api-key"
            else:
                from django.core.exceptions import ValidationError

                raise ValidationError(f"FIREBASE_API_KEY is required")

        if not config.sms.api_key:
            # Check if running tests
            import sys

            if "test" in sys.argv:
                config.sms.api_key = "test-sms-api-key"
            else:
                from django.core.exceptions import ValidationError

                raise ValidationError(f"SMS_API_KEY is required")

        return config

    except ValidationError as e:
        logger.error(f"Configuration validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def get_django_settings() -> Dict[str, Any]:
    """
    Convert the configuration to Django settings format.

    Returns:
        Dict[str, Any]: Dictionary of Django settings.
    """
    config = get_config()

    return {
        "DEBUG": config.debug,
        "SECRET_KEY": config.secret_key,
        "ALLOWED_HOSTS": config.allowed_hosts,
        "DATABASES": {
            "default": {
                "ENGINE": config.database.engine,
                "NAME": config.database.name,
                "HOST": config.database.host,
                "PORT": config.database.port,
                "USER": config.database.user,
                "PASSWORD": config.database.password,
                "OPTIONS": {
                    "timeout": config.database.timeout,
                },
            }
        },
        "CACHES": {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache"
                if config.cache.use_redis
                else "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": config.cache.redis_url
                if config.cache.use_redis
                else "unique-snowflake",
                "OPTIONS": {
                    "retry_on_timeout": True,
                    "max_connections": config.cache.max_connections,
                },
                "KEY_PREFIX": config.cache.key_prefix,
                "TIMEOUT": config.cache.timeout,
            }
        },
        "EMAIL_BACKEND": config.email.backend,
        "DEFAULT_FROM_EMAIL": config.email.default_from_email,
        "EMAIL_HOST": config.email.host,
        "EMAIL_PORT": config.email.port,
        "EMAIL_HOST_USER": config.email.username,
        "EMAIL_HOST_PASSWORD": config.email.password,
        "EMAIL_USE_TLS": config.email.use_tls,
        "FIREBASE_API_KEY": config.firebase.api_key,
        "FIREBASE_AUTH_DOMAIN": config.firebase.auth_domain,
        "FIREBASE_PROJECT_ID": config.firebase.project_id,
        "FIREBASE_STORAGE_BUCKET": config.firebase.storage_bucket,
        "FIREBASE_MESSAGING_SENDER_ID": config.firebase.messaging_sender_id,
        "FIREBASE_APP_ID": config.firebase.app_id,
        "FIREBASE_MEASUREMENT_ID": config.firebase.measurement_id,
        "SMS_API_KEY": config.sms.api_key,
        "SMS_SENDER_ID": config.sms.sender_id,
        "GUNICORN_WORKERS": config.gunicorn.workers,
        "GUNICORN_THREADS": config.gunicorn.threads,
        "GUNICORN_TIMEOUT": config.gunicorn.timeout,
        "GUNICORN_KEEPALIVE": config.gunicorn.keepalive,
    }
