import os


class Config:
    AI_PROVIDER     = os.environ.get("AI_PROVIDER",     "anthropic")
    ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL",  "claude-sonnet-4-5")
    OPENAI_KEY      = os.environ.get("OPENAI_API_KEY",   "")
    OPENAI_MODEL    = os.environ.get("OPENAI_MODEL",     "gpt-4o")
    SQLITE_PATH     = os.environ.get("SQLITE_PATH",      "./data/analytics.db")
    CSV_PATH        = os.environ.get("CSV_PATH",         "./data/superstore.csv")
    CORS_ORIGINS    = os.environ.get("CORS_ORIGINS",     "*").split(",")
    SECRET_KEY      = os.environ.get("SECRET_KEY",       "dev-secret-key")
    FLASK_ENV       = os.environ.get("FLASK_ENV",        "production")
