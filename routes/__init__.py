from fastapi import FastAPI

from .hello import router as hello_router


def register_routes(app: FastAPI):
    app.include_router(hello_router, prefix='/hello', tags=['hello'])
