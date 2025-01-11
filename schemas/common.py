from enum import Enum
from typing import TypeVar, Generic, List, Optional, get_origin, get_args
from pydantic import BaseModel, Field, model_validator

T = TypeVar('T')
T_BaseModel = TypeVar('T_BaseModel', bound=BaseModel)


class PageParams(BaseModel):
    page: int = Field(1, description='页码')
    size: int = Field(20, description='每页条数')

    # 将 @model_validator 添加到父类的子类，转换枚举字段为整数
    @model_validator(mode='before')
    def convert_enum_to_int(cls, values):
        __annotations__ = cls.__annotations__
        for field, value in values.items():
            try:
                annotation = __annotations__.get(field)
                if not annotation:
                    continue
                _type = get_args(annotation) if get_origin(annotation) else annotation
                _type = _type if isinstance(_type, tuple) else (_type,)
                if any(issubclass(t, Enum) for t in _type):
                    values[field] = int(value)
            except Exception:  # noqa
                continue
        return values


class EResponseCode:
    """响应码"""

    SUCCESS = 0
    FAILED = 400
    UN_AUTH = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    PARAMS_ERR = 422
    SERVER_ERR = 500
    NOT_IMPL = 501


class PaginateResult(BaseModel, Generic[T]):
    """分页响应模型"""

    total: int = Field(title='总条数')
    items: List[T] = Field(title='数据列表')
    page: int
    size: int
    pages: int


class BaseResponse(BaseModel, Generic[T]):
    """响应包装模型"""

    code: int = Field(title='状态码')
    msg: str = Field(title='消息')
    data: Optional[T] = Field(None, title='数据')

    @classmethod
    def make(cls, data: Optional[T] = None, **kwargs):
        return cls(data=data, **kwargs)


class SuccessResponse(BaseResponse[T]):
    """成功响应模型"""

    code: Optional[int] = Field(EResponseCode.SUCCESS, title='状态码')
    msg: Optional[str] = Field('操作成功', title='消息')


class FailResponse(BaseResponse[T]):
    """失败响应模型"""

    code: int = Field(title='状态码')
    msg: Optional[str] = Field('操作失败', title='消息')
