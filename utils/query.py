from typing import Optional, Type, List, Union

from sqlalchemy import select, func, Select, Row
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from schemas.common import T_BaseModel, PageParams, PaginateResult
from utils.connect import T_TableBase


async def get_one(db: AsyncSession, entity: Type[T_TableBase], **filter_by) -> Optional[T_TableBase]:
    """通用查询一条记录"""
    result = await db.execute(select(entity).filter_by(**filter_by))
    return result.scalar_one_or_none()


async def get_one_with_del(db: AsyncSession, entity: Type[T_TableBase], **filter_by):
    """通用查询一条未删除的记录"""
    filter_by.setdefault('is_del', False)
    return await get_one(db, entity, **filter_by)


async def get_parsed_one(
    db: AsyncSession,
    query: Select,
    schema: Type[T_BaseModel] = None,
) -> Union[T_BaseModel, dict]:
    """通用查询一条记录"""
    result = await db.execute(query)
    val = result.one_or_none()
    if not val:
        return None
    return parse_row(val, query=query, schema=schema)


async def get_parsed_many(
    db: AsyncSession,
    query: Select,
    schema: Type[T_BaseModel] = None,
) -> List[Union[T_BaseModel, dict]]:
    """通用查询多条记录"""
    result = await db.execute(query)
    return [parse_row(row, query=query, schema=schema) for row in result.all()]


async def paginate_query(
    db: AsyncSession,
    query: Select,
    page_params: PageParams,
    schema: Type[T_BaseModel] = None,
) -> PaginateResult[Union[T_BaseModel, dict]]:
    """通用分页查询"""
    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query) or 0

    if total == 0:
        # 无数据直接返回空分页结果
        return PaginateResult(
            items=[],
            total=0,
            page=page_params.page,
            size=page_params.size,
            pages=0,
        )

    # 分页
    offset = (page_params.page - 1) * page_params.size
    result_list = await get_parsed_many(
        db,
        query=query.offset(offset).limit(page_params.size),
        schema=schema,
    )
    return PaginateResult(
        items=result_list,
        total=total,
        page=page_params.page,
        size=page_params.size,
        pages=(total + page_params.size - 1) // page_params.size,
    )


def parse_row(
    row: Row,
    *,
    query: Select = None,
    query_keys: List[str] = None,
    schema: Type[T_BaseModel] = None,
):
    """解析行数据，将元组或复杂对象解析为字典"""
    try:
        # 提取列名
        if query is None and query_keys is None:
            raise ValueError('query or query_keys must be provided')
        query_keys = query_keys or [c.name for c in query.c]
        parsed = {}
        key_index = 0
        row = row if hasattr(row, '__iter__') else (row,)
        # # 如果是只查某个实体，则直接返回
        # if len(row) == 1 and schema is None and isinstance(row[0], TableBase):
        #     return row[0]
        for item in row:
            if hasattr(item, 'to_dict'):  # 如果对象有 to_dict 方法
                dic = item.to_dict()
                parsed.update(dic)
                key_index += len(dic)
            else:
                name = query_keys[key_index]
                is_list = name.endswith('.list')
                name = name[:-5] if is_list else name
                if is_list:
                    item = item.split(settings.ZERO_WORD) if item else []
                parsed[name] = item
                key_index += 1
        return schema(**parsed) if schema else parsed
    except IndexError:
        raise ValueError(f'Row data does not match query keys: {query_keys}')
