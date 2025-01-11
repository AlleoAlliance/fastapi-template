from typing import Optional, List

from fastapi import Depends

from crud.project import get_project_dtl
from entities import User, Project
from utils.connect import get_async_db, AsyncSession
from utils.errors import Http403Forbidden, Http401Unauthorized
from utils.security import OAUTH2_SCHEME
from fastapi import Request


async def get_adb():
    async with get_async_db() as db:
        yield db


async def get_current_user(token: str = Depends(OAUTH2_SCHEME), db=Depends(get_adb)):
    """获取当前登录用户"""
    from crud.user import get_user_by_token

    return await get_user_by_token(db, token)


async def get_project_id(request: Request):
    ph = request.headers.get('x-project-id', None)
    if not ph or not ph.isdigit():
        return
    return int(ph)


async def get_current_project(
    project_id: int = Depends(get_project_id),
    db: AsyncSession = Depends(get_adb),
    user: User = Depends(get_current_user),
):
    from crud.project import get_project_user

    if not project_id:
        # 低权限的必须要选择项目才能登录
        if not user.role_id:
            raise Http401Unauthorized('权限不足，请重新登录')
        return None
    pu = await get_project_user(db, project_id, user.id)
    if not pu:
        raise Http403Forbidden('没有权限访问该项目')
    return await get_project_dtl(db, id=project_id)


class PermissionChecker:
    def __init__(self, code: str = None):
        self._first_code = code
        self._user = None
        self._db = None
        self._project = None
        self._permissions = None

    async def __call__(
        self,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_adb),
        project: Project = Depends(get_current_project),
    ):
        from crud.role import get_user_permissions, UserPermissionQuery

        self._user = user
        self._db = db
        self._project = project
        upq = UserPermissionQuery(uid=self._user.id)
        if self._project:
            upq.project_id = self._project.id
        if not self._permissions:
            permissions = await get_user_permissions(self._db, upq)
            self._permissions = permissions
        if self._first_code:
            self.check(self._first_code)
            return self
        return self

    def check(self, code: str, raise_=True):
        from utils.permissions import check_permission

        if not check_permission(code, self._permissions):
            if raise_:
                raise self.check_err
            return False
        return True

    def check_cross_project(self, project_id: int = None, sys_code: str = None):
        """
        1. 判断是否有系统权限或者在当前项目
        2. 当存在跨项目权限时返回None, 否则返回当前项目ID
        :return:
        """
        if sys_code and self.check(sys_code, False):
            return None
        if not self._project:
            raise self.check_err
        if project_id and self._project.id != project_id:
            raise self.check_err
        return self.project_id

    @property
    def check_err(self):
        return Http403Forbidden('权限不足')

    @property
    def permissions(self) -> List[str]:
        return self._permissions or []

    @property
    def project(self) -> Optional[Project]:
        return self._project

    @property
    def project_id(self) -> Optional[int]:
        return self._project.id if self._project else None

    @property
    def user(self) -> Optional[User]:
        return self._user

    @property
    def user_id(self) -> Optional[int]:
        return self.user.id if self.user else None

    @property
    def db(self) -> AsyncSession:
        return self._db
