"""
@Created on : 2025/12/8
@Author: wrn
@Des: 电影相关路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from tortoise.exceptions import IntegrityError
from models.movies import Movie
from schemas import MovieCreate, MovieUpdate, Movie_Pydantic
from core.security import get_current_user



# 全局鉴权，只有登录用户才能操作
movies = APIRouter(tags=["电影相关"], dependencies=[Depends(get_current_user)])


@movies.get("/movies", summary="获取电影列表", response_model=list[Movie_Pydantic])

async def movie_list(limit: int = 10, page: int = 1):

    skip = (page - 1) * limit
    return await Movie_Pydantic.from_queryset(
        Movie.all().offset(skip).limit(limit).order_by("-id")

    )


@movies.post("/movies", summary="新增电影", status_code=status.HTTP_201_CREATED, response_model=Movie_Pydantic)

async def movie_create(movie_form: MovieCreate):
    try:

        movie_obj = await Movie.create(**movie_form.model_dump())
        return await Movie_Pydantic.from_tortoise_orm(movie_obj)
    
    except IntegrityError:

        raise HTTPException(status_code=400, detail="创建失败，可能包含重复数据")


@movies.delete("/movies/{movie_id}", summary="删除电影", status_code=status.HTTP_200_OK)


async def movie_delete(movie_id: int): 

    deleted_count = await Movie.filter(id=movie_id).delete()
    
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"电影 ID {movie_id} 不存在")
    
    return {"code": 200, "msg": "删除成功", "deleted_id": movie_id}


@movies.put("/movies/{movie_id}", summary="更新电影", response_model=Movie_Pydantic)

async def movie_update(movie_id: int, movie_form: MovieUpdate): 
    # 1. 提取更新数据
    updated_data = movie_form.model_dump(exclude_unset=True)
    
    if not updated_data:
        return await Movie_Pydantic.from_queryset_single(Movie.get(id=movie_id))

    # 2. 执行更新

    updated_count = await Movie.filter(id=movie_id).update(**updated_data)
    
    if not updated_count:
        raise HTTPException(status_code=404, detail=f"电影 ID {movie_id} 不存在")

    return await Movie_Pydantic.from_queryset_single(Movie.get(id=movie_id))


__all__ = [
    "movies"
]