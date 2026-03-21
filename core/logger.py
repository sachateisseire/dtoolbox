import logging
import os

_logger = None


def setup_logger():
    global _logger

    if _logger:
        return _logger

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename="logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    _logger = logging.getLogger("app")
    return _logger