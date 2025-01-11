#!/bin/sh

echo '切换到工作目录'
cd /app

echo '添加脚本执行权限'
chmod +x wait-for-it.sh

# 等待 MySQL 启动并且健康
echo '等待 MySQL 启动...'
./wait-for-it.sh mysql:3306 --timeout=60 --strict -- echo 'MySQL 启动成功'

# 等待 Redis 启动并且健康
echo '等待 Redis 启动...'
./wait-for-it.sh redis:6379 --timeout=60 --strict -- echo 'Redis 启动成功'

echo '创建日志文件夹'
mkdir -p logs

echo '同步数据库'
alembic upgrade head

echo "启动 web 服务"
gunicorn -k uvicorn.workers.UvicornWorker -c gunicorn.conf.py main:app
