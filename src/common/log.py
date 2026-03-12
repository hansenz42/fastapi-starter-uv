#!/usr/bin/env python3
import os
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from src.common.env import config

__all__ = ["get_logger"]


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter"""

    # Standard LogRecord attributes
    STANDARD_ATTRS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
        "asctime",
    }

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }

        # If exception info exists, add it to the log
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (passed via the `extra` parameter)
        for attr in dir(record):
            if not attr.startswith("_") and attr not in self.STANDARD_ATTRS:
                value = getattr(record, attr)
                if not callable(value):  # only add non-callable attributes
                    log_data[attr] = value

        return json.dumps(log_data, ensure_ascii=False)


class DailyRotatingFileHandler(logging.FileHandler):
    """Daily rotating file handler: current log is always `log.json`, backups include the date"""

    def __init__(self, log_file: Path, backup_count: int = 7, encoding: str = "utf-8"):
        self.log_file = log_file
        self.backup_count = backup_count
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        super().__init__(str(log_file), encoding=encoding)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record and check whether rotation is needed"""
        # Check if the date has changed
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self._rollover(new_date)

        super().emit(record)

    def _rollover(self, new_date: str) -> None:
        """Rotate the log file: backup the old file and create a new one"""
        old_date = self.current_date
        self.current_date = new_date

        # Close the current file handler
        self.close()

        # Backup the log file for the old date
        backup_file = self.log_file.parent / f"{self.log_file.name}.{old_date}"
        if self.log_file.exists():
            self.log_file.rename(backup_file)

        # Clean up backup files exceeding `backup_count` days
        self._cleanup_old_files()

        # Open a new log file
        self._open()

    def _cleanup_old_files(self) -> None:
        """Remove old log files that exceed retention days"""
        log_dir = self.log_file.parent
        pattern = re.compile(rf"^{self.log_file.name}\.\d{{4}}-\d{{2}}-\d{{2}}$")

        backup_files = [
            f for f in log_dir.glob(f"{self.log_file.name}.*") if pattern.match(f.name)
        ]

        # Sort by filename (which includes the date)
        backup_files.sort(reverse=True)

        # Delete files beyond the configured `backup_count`
        for old_file in backup_files[self.backup_count :]:
            try:
                old_file.unlink()
            except Exception:
                pass


def get_logger(module_name: str, propagate: bool = False) -> logging.Logger:
    """Configure and return a logger

    Args:
        module_name: Name of the module for logger identification
        propagate: Whether to propagate logs to parent logger (default: False)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger object
    logger = logging.getLogger(module_name)
    logger.setLevel(config.log_level)
    logger.propagate = propagate

    # If the logger already has handlers, it's already configured — return it
    if logger.handlers:
        return logger

    # Configure console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # If LOG_DIR is configured, add JSON formatted file output
    if config.log_dir:
        log_dir = Path(config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # The log file is always `log.json`; backups will be `log.json.YYYY-MM-DD`
        log_file = log_dir / "log.json"

        # Use the custom daily rotating handler
        # - Current logs are always written to `log.json` (convenient for collectors)
        # - Backups are named `log.json.YYYY-MM-DD`
        # - Keep backups for 7 days
        file_handler = DailyRotatingFileHandler(log_file, backup_count=7)
        file_handler.setLevel(config.log_level)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger
