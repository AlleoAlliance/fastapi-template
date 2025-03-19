> Generic single-database configuration.

### 初始化 alembic

```bash
alembic init
# 初始化异步版本
alembic init -t async aioalembic
```

### 修订数据库版本

```bash
# --autogenerate 表示自动生成迁移脚本
# -m 表示添加注释
alembic revision -m "add test tables"
alembic revision --autogenerate -m "create all tables"
```

### 升级数据库版本

```bash
# head 表示升级到最新版本
alembic upgrade head
```

### 降级数据库版本

```bash
# -1 表示降级一个版本
alembic downgrade -1
```
