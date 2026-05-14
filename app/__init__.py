import logging
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from app.config import Config

load_dotenv()

def configure_logging():
    log_level = logging.DEBUG if os.environ.get("FLASK_ENV") == "development" else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def create_app(config: Config | None = None) -> Flask:
    configure_logging()
    app = Flask(__name__)

    cfg = config or Config()
    app.config.from_object(cfg)

    CORS(app, origins=cfg.CORS_ORIGINS)

    from app.routes.conversations import conversations_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(conversations_bp)
    app.register_blueprint(chat_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
