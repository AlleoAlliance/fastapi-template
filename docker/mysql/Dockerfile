# 使用基础镜像
FROM mysql:5.7

# 设置工作目录
WORKDIR /

# 复制配置文件
COPY my.cnf /etc/mysql/conf.d/my.cnf

# 启动命令
CMD ["mysqld", "--character-set-server=utf8", "--collation-server=utf8_unicode_ci"]
