import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger
from starlette.staticfiles import StaticFiles
from os.path import dirname, join

from config import settings
from schemas.common import FailResponse, EResponseCode
from routes import register_routes
from utils.errors import get_response_mapper

app = FastAPI(
    root_path=settings.API_V1_PREFIX,
    responses=get_response_mapper(),
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    # 检查是否开启API文档
    **({} if settings.ENABLE_API_DOCS else dict(openapi_url=None, docs_url=None, redoc_url=None)),
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
register_routes(app)

STATIC_DIR = join(dirname(__file__), 'static')
app.mount('/', StaticFiles(directory=STATIC_DIR, html=True))


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, error: HTTPException):
    return JSONResponse(
        status_code=error.status_code,
        content=FailResponse(msg=error.detail, code=error.status_code).model_dump(),
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, errors: list):
    if settings.IS_DEV:
        logger.warning(errors)
    return JSONResponse(
        status_code=EResponseCode.PARAMS_ERR,
        content=FailResponse(msg='参数错误', code=EResponseCode.PARAMS_ERR).model_dump(),
    )


@app.exception_handler(Exception)
def unexpected_exception_handler(request: Request, exc: Exception):
    if settings.IS_PROD:
        stack_trace = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        logger.error(f'未经处理的异常: {stack_trace}')
    return JSONResponse(
        status_code=EResponseCode.SERVER_ERR,
        content=FailResponse(msg='服务异常，请稍后重试', code=EResponseCode.SERVER_ERR).model_dump(),
    )
