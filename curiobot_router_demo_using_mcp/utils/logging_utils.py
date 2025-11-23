import os
import pathlib
import logging
import logging.config


class LoggerFactory:
    """Centralised logging configuration and logger factory.

    Call LoggerFactory.configure() once at startup, then use get_logger(name).
    """
    _configured = False

    @classmethod
    def configure(cls) -> None:
        if cls._configured:
            return

        project_root = pathlib.Path(os.getcwd())
        log_dir = project_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE", str(log_dir / "curiobot.log"))

        LOGGING = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "std": {
                    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "std",
                    "level": level,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": log_file,
                    "maxBytes": 10 * 1024 * 1024,
                    "backupCount": 5,
                    "formatter": "std",
                    "level": level,
                },
            },
            "root": {
                "handlers": ["console", "file"],
                "level": level,
            },
        }

        logging.config.dictConfig(LOGGING)
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        if not cls._configured:
            cls.configure()
        return logging.getLogger(name)


class TraceContext:
    """Minimal stub – extend if you want structured tracing later."""
    def __init__(self, **fields):
        self.fields = fields

    def __repr__(self) -> str:
        return f"TraceContext({self.fields!r})"
