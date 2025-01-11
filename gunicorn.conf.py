import logging
from logging.handlers import TimedRotatingFileHandler

# 基础日志配置
loglevel = 'debug'
workers = 4
bind = '0.0.0.0:8000'

# 配置日志分割
log_dir = '/app/logs'

access_log_handler = TimedRotatingFileHandler(
    f'{log_dir}/access.log',
    when='midnight',
    interval=1,
    backupCount=7,
    encoding='utf-8',
)
access_log_handler.suffix = '%Y-%m-%d'
access_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

error_log_handler = TimedRotatingFileHandler(
    f'{log_dir}/error.log',
    when='midnight',
    interval=1,
    backupCount=7,
    encoding='utf-8',
)
error_log_handler.suffix = '%Y-%m-%d'
error_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))

# 绑定日志处理器
logging.getLogger('gunicorn.access').addHandler(access_log_handler)
logging.getLogger('gunicorn.error').addHandler(error_log_handler)
