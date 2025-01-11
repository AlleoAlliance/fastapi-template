# 基于FastAPI后端模板

## 技术栈

- Python 3.9
- FastAPI
- Pydantic
- SQLAlchemy
- alembic
- aiomysql
- redis.asyncio

## 使用方法

- 克隆项目到本地

```bash
git clone https://github.com/AlleoAlliance/fastapi-template.git
```

- 使用该项目之前，请确保你的环境中已经安装了Python 3.9。
- 在项目根目录下，运行以下命令安装依赖：（推荐使用[虚拟环境](https://docs.python.org/3/library/venv.html)）

```bash
pip install -r requirements.txt
```

- 在安装环境后，你需要执行[make_env_from_settings.py](scripts/make_env_from_settings.py)脚本来初始化配置文件

```bash
python scripts/make_env_from_settings.py -f
# 你也可以 使用 -h 查看帮助信息
python scripts/make_env_from_settings.py -h
```

- 生成配置文件后，你应该能得到`.env.dev`,`.env.test`,`.env.prod`这三个文件
- **注意**：
- `.env.dev`是开发环境配置文件，`.env.test`是测试环境配置文件，`.env.prod`是生产环境配置文件
- 他们会在对应的环境下自动加载，所以你只需要在对应的环境下修改对应的配置文件即可
- 此时你需要检查**生成的配置文件**，将带有`(*REQUIRED)`标记的填上对应的值，否则项目无法启动。
- 现在你可以启动你的应用了，在项目根目录下，运行以下命令启动应用：

### 开发环境

以开发模式启动

```bash
uvicorn main:app --reload
```

- 使用`--reload`选项可以使服务器在代码改变时自动重新加载。

- 打开浏览器访问 `http://127.0.0.1:8000/` ，你应该会看到页面显示 **Hello fastapi-template _static_**
- 打开浏览器访问 `http://127.0.0.1:8000/api/v1/hello` ，你应该会看到页面显示

```json
{
  "code": 0,
  "msg": "this is message",
  "data": "fastapi-template!"
}
```

### 数据库管理
- 数据库迁移
- 在项目根目录下，运行以下命令进行数据库迁移：
- 具体命令可以查看 [aioalembic/README.md](aioalembic/README.md)

```bash
alembic upgrade head
```


### 测试环境

以测试环境启动

```bash
pytest
```

### 生产环境

#### Docker部署（推荐）

- 项目中已经存在基本的 `docker-compose.yml` 文件，你可以直接使用它来部署你的应用。
- 在使用之前将 `docker-compose.yml` 内部的 `xxxx` 替换成实际的值。一般是一些数据库名密码等
- 然后直接执行以下命令即可

```bash
docker-compose up -d
```

#### 通过gunicorn部署

你可以创建一个`gunicorn`启动命令：

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

这里`-w 4`意味着使用4个工作进程，`-k uvicorn.workers.UvicornWorker`指定使用Uvicorn的工作器。
