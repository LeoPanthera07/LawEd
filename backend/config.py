from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "change-me-in-production-use-secrets-token-hex-32"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    DATABASE_URL: str = "postgresql+asyncpg://nyayasetu:password@localhost:5432/nyayasetu"
    TEST_DATABASE_URL: str = "postgresql+asyncpg://test_user:test_pass@localhost:5433/nyayasetu_test"

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "nyayasetu_clauses"
    QDRANT_API_KEY: str = ""

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "nyayasetu_dev"

    EMBEDDING_MODEL_NAME: str = "intfloat/multilingual-e5-large"
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DEVICE: str = "cpu"

    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    SMTP_HOST: str = "smtp.sendgrid.net"
    SMTP_PORT: int = 587
    SMTP_USER: str = "apikey"
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@nyayasetu.in"
    EMAIL_FROM_NAME: str = "NyayaSetu"

    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    RATE_LIMIT_UNAUTHENTICATED: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "30/minute"

    CONFIDENCE_ESCALATION_THRESHOLD: float = 0.45
    CONFIDENCE_WARNING_THRESHOLD: float = 0.60
    FREE_TIER_MONTHLY_LIMIT: int = 3
    QDRANT_TOP_K_PER_QUERY: int = 5
    NEO4J_TRAVERSAL_DEPTH: int = 2
    MAX_CLAUSES_RETURNED: int = 10

    FF_WRITEUP_ENABLED: bool = True
    FF_GUEST_MODE: bool = True
    FF_GRAPH_TRAVERSAL: bool = True
    FF_PAYMENT_REQUIRED: bool = True
    FF_ESCALATION_ENABLED: bool = True

    ALERT_EMAIL: str = ""
    ADMIN_EMAIL: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
