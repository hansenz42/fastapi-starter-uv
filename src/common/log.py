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
    """自定义 JSON 格式化器"""

    # LogRecord 的标准属性
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

        # 如果有异常信息，添加到日志中
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # 添加额外的字段（通过 extra 参数传递的）
        for attr in dir(record):
            if not attr.startswith("_") and attr not in self.STANDARD_ATTRS:
                value = getattr(record, attr)
                if not callable(value):  # 只添加非方法属性
                    log_data[attr] = value

        return json.dumps(log_data, ensure_ascii=False)


class DailyRotatingFileHandler(logging.FileHandler):
    """按天轮转的日志处理器，当前日志始终为 log.json，备份文件名带日期"""

    def __init__(self, log_file: Path, backup_count: int = 7, encoding: str = "utf-8"):
        self.log_file = log_file
        self.backup_count = backup_count
        self.current_date = datetime.now().strftime("%Y-%m-%d")

        super().__init__(str(log_file), encoding=encoding)

    def emit(self, record: logging.LogRecord) -> None:
        """发送日志记录，检查是否需要轮转"""
        # 检查日期是否变化
        new_date = datetime.now().strftime("%Y-%m-%d")
        if new_date != self.current_date:
            self._rollover(new_date)

        super().emit(record)

    def _rollover(self, new_date: str) -> None:
        """轮转日志文件：备份旧文件，创建新文件"""
        old_date = self.current_date
        self.current_date = new_date

        # 关闭当前文件处理器
        self.close()

        # 备份旧日期的日志文件
        backup_file = self.log_file.parent / f"{self.log_file.name}.{old_date}"
        if self.log_file.exists():
            self.log_file.rename(backup_file)

        # 清理超过 backup_count 天的备份文件
        self._cleanup_old_files()

        # 打开新的日志文件
        self._open()

    def _cleanup_old_files(self) -> None:
        """删除超过保留天数的旧日志文件"""
        log_dir = self.log_file.parent
        pattern = re.compile(rf"^{self.log_file.name}\.\d{{4}}-\d{{2}}-\d{{2}}$")

        backup_files = [
            f for f in log_dir.glob(f"{self.log_file.name}.*") if pattern.match(f.name)
        ]

        # 按文件名排序，文件名中包含日期
        backup_files.sort(reverse=True)

        # 删除超过 backup_count 的文件
        for old_file in backup_files[self.backup_count :]:
            try:
                old_file.unlink()
            except Exception:
                pass


def get_logger(module_name: str, propagate: bool = False) -> logging.Logger:
    """
    设置日志配置

    Args:
        module_name: 模块名称，用于日志标识
        propagate: 是否传播日志到父级logger，默认为False

    Returns:
        logging.Logger: 配置好的日志对象
    """
    # 创建logger对象
    logger = logging.getLogger(module_name)
    logger.setLevel(config.log_level)
    logger.propagate = propagate

    # 如果logger已经有处理器，说明已经配置过，直接返回
    if logger.handlers:
        return logger

    # 配置控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 如果配置了 LOG_DIR，则添加 JSON 格式的文件输出
    if config.log_dir:
        log_dir = Path(config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # 日志文件始终为 log.json，备份文件为 log.json.YYYY-MM-DD
        log_file = log_dir / "log.json"

        # 使用自定义的按天轮转处理器
        # - 当前日志始终写入 log.json（便于 sls 采集）
        # - 轮转时备份为 log.json.YYYY-MM-DD
        # - 保留 7 天的备份文件
        file_handler = DailyRotatingFileHandler(log_file, backup_count=7)
        file_handler.setLevel(config.log_level)
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger
