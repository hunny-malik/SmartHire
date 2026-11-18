import logging
import sys
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "endpoint"):
            log_obj["endpoint"] = record.endpoint
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

def get_logger(name: str = "smarthire") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s in %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("smarthire")
