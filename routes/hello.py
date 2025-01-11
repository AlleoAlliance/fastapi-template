from fastapi import APIRouter

from schemas.common import SuccessResponse

router = APIRouter()


@router.get('')
async def hello():
    return SuccessResponse.make('fastapi-template!', msg='this is message')
