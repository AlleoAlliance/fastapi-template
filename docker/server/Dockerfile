# 使用基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目代码到工作目录
COPY . .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 启动命令
CMD ["sh", "entrypoint.sh"]
