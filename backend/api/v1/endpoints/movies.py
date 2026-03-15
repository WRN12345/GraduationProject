"""
@Created on : 2025/12/8
@Author: wrn
@Des: 电影相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from schemas import MovieCreate, MovieUpdate, Movie_Pydantic
from core.security import get_current_user
from services.movie_service import movie_service


# 全局鉴权，只有登录用户才能操作
movies = APIRouter(tags=["电影相关"], dependencies=[Depends(get_current_user)])


@movies.get("/movies", summary="获取电影列表", response_model=list[Movie_Pydantic])
async def movie_list(limit: int = 10, page: int = 1):
    """获取电影列表"""
    result = await movie_service.get_movie_list(limit=limit, page=page)
    return result


@movies.post("/movies", summary="新增电影", status_code=status.HTTP_201_CREATED, response_model=Movie_Pydantic)
async def movie_create(movie_form: MovieCreate):
    """创建电影"""
    result = await movie_service.create_movie(
        name=movie_form.name,
        year=movie_form.year
    )

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@movies.delete("/movies/{movie_id}", summary="删除电影", status_code=status.HTTP_200_OK)
async def movie_delete(movie_id: int):
    """删除电影"""
    result = await movie_service.delete_movie(movie_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@movies.put("/movies/{movie_id}", summary="更新电影", response_model=Movie_Pydantic)
async def movie_update(movie_id: int, movie_form: MovieUpdate):
    """更新电影"""
    result = await movie_service.update_movie(
        movie_id=movie_id,
        name=movie_form.name,
        year=movie_form.year
    )

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


__all__ = [
    "movies"
]