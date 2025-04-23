import sys
import logging
import json
from loguru import logger as loguru_logger
from pathlib import Path

from src.utils.config import settings

# Configure Loguru logger
LOG_LEVEL = settings.LOG_LEVEL
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure Loguru
loguru_logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "format": LOG_FORMAT,
            "level": LOG_LEVEL,
            "colorize": True,
        },
        {
            "sink": log_dir / "app.log",
            "format": LOG_FORMAT,
            "level": LOG_LEVEL,
            "rotation": "10 MB",
            "retention": "1 month",
            "compression": "zip",
        },
        {
            "sink": log_dir / "errors.log",
            "format": LOG_FORMAT,
            "level": "ERROR",
            "rotation": "10 MB",
            "retention": "1 month",
            "compression": "zip",
        },
    ]
)

# Intercept standard library logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = loguru_logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        loguru_logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

# Setup interception
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# Intercept uvicorn logs
for logger_name in ["uvicorn", "uvicorn.error", "fastapi"]:
    intercept_logger = logging.getLogger(logger_name)
    intercept_logger.handlers = [InterceptHandler()]

# Export logger
logger = loguru_logger 