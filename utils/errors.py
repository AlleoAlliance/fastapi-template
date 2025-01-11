import re
from typing import Type

from fastapi import HTTPException, status
from pydantic import Field
from http import HTTPStatus

from schemas.common import FailResponse

"""
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_402_PAYMENT_REQUIRED = 402
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_406_NOT_ACCEPTABLE = 406
HTTP_407_PROXY_AUTHENTICATION_REQUIRED = 407
HTTP_408_REQUEST_TIMEOUT = 408
HTTP_409_CONFLICT = 409
HTTP_410_GONE = 410
HTTP_411_LENGTH_REQUIRED = 411
HTTP_412_PRECONDITION_FAILED = 412
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_414_REQUEST_URI_TOO_LONG = 414
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415
HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE = 416
HTTP_417_EXPECTATION_FAILED = 417
HTTP_418_IM_A_TEAPOT = 418
HTTP_421_MISDIRECTED_REQUEST = 421
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_423_LOCKED = 423
HTTP_424_FAILED_DEPENDENCY = 424
HTTP_425_TOO_EARLY = 425
HTTP_426_UPGRADE_REQUIRED = 426
HTTP_428_PRECONDITION_REQUIRED = 428
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE = 431
HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS = 451
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_501_NOT_IMPLEMENTED = 501
HTTP_502_BAD_GATEWAY = 502
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_504_GATEWAY_TIMEOUT = 504
HTTP_505_HTTP_VERSION_NOT_SUPPORTED = 505
HTTP_506_VARIANT_ALSO_NEGOTIATES = 506
HTTP_507_INSUFFICIENT_STORAGE = 507
HTTP_508_LOOP_DETECTED = 508
HTTP_510_NOT_EXTENDED = 510
HTTP_511_NETWORK_AUTHENTICATION_REQUIRED = 511
"""


class Http400BadRequest(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class Http401Unauthorized(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        headers = (headers or {'WWW-Authenticate': 'Bearer'},)
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)


class Http403Forbidden(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, headers)


class Http404NotFound(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class Http422ProcessableEntity(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, headers)


class Http500ServerError(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail, headers)


class Http501NotImplemented(HTTPException):
    def __init__(self, detail: str = None, headers=None):
        super().__init__(status.HTTP_501_NOT_IMPLEMENTED, detail, headers)


HTTP_ERROR_CLASS_RE = re.compile(r'Http(?P<code>\d+)(\w+)')


# 动态生成新的类并覆盖 `code` 字段
def create_fail_response_class(error_code: int) -> Type[FailResponse[None]]:
    """根据错误码动态生成新的 FailResponse 类"""
    class_dict = {
        'code': Field(error_code, title='状态码'),
        'msg': Field(HTTPStatus(error_code).phrase, title='错误消息'),
        '__annotations__': {'code': int, 'msg': str},
    }
    # 动态创建一个新的类，继承 FailResponse，并覆盖 code 字段
    return type(f'Http{error_code}Response', (FailResponse[None],), class_dict)


def get_response_mapper():
    """获取 HTTPException 的映射器"""
    ret = dict()
    for name, value in globals().items():
        result = HTTP_ERROR_CLASS_RE.match(name)
        if result is None and not isinstance(value, HTTPException):
            continue
        code = int(result.group('code'))
        ret[code] = dict(
            model=create_fail_response_class(code),
            response_model_exclude_none=True,
        )
    return ret
