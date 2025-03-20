import logging
from logging.handlers import RotatingFileHandler

from config import settings


logger = logging.getLogger(settings.PROJECT_NAME)
logger.setLevel(logging.INFO if settings.IS_PROD else logging.DEBUG)
formatter = logging.Formatter(
    fmt='%(asctime)s.%(msecs)03d %(levelname)-7s [%(process)d] %(module)s:%(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

if settings.IS_PROD:
    # 文件输出（自动轮转）
    from os import path, makedirs

    log_dir = path.join(settings.PROJECT_ROOT, 'logs')
    path.exists(log_dir) or makedirs(log_dir)
    log_filename = settings.PROJECT_NAME.lower().replace(' ', '_') + '.log'
    file_handler = RotatingFileHandler(
        filename=path.join(log_dir, log_filename),
        maxBytes=10 * 1024 * 1024,  # 10MB,
        backupCount=10,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

__all__ = ['logger']
