"""
@Created on : 2026/3/15
@Author: wrn
@Des: 电影服务 - Movie 业务逻辑层
"""
from typing import List, Optional, Dict, Any
from tortoise.exceptions import IntegrityError
from models.movies import Movie
import logging

logger = logging.getLogger(__name__)


class MovieService:
    """电影服务 - Movie CRUD 操作"""

    async def get_movie_list(
        self,
        limit: int = 10,
        page: int = 1
    ) -> dict:
        """
        获取电影列表

        Args:
            limit: 每页数量
            page: 页码

        Returns:
            dict: 包含电影列表的字典
        """
        skip = (page - 1) * limit
        movies = await Movie.all().offset(skip).limit(limit).order_by("-id")

        # 转换为字典列表
        movies_data = [
            {
                "id": movie.id,
                "name": movie.name,
                "year": movie.year,
                "created_at": movie.created_at,
                "updated_at": movie.updated_at
            }
            for movie in movies
        ]

        return movies_data

    async def create_movie(
        self,
        name: str,
        year: int
    ) -> dict:
        """
        创建电影

        Args:
            name: 电影名称
            year: 上映年份

        Returns:
            dict: 创建的电影数据

        Raises:
            Returns {"error": "..."} on failure
        """
        try:
            movie_obj = await Movie.create(name=name, year=year)

            return {
                "id": movie_obj.id,
                "name": movie_obj.name,
                "year": movie_obj.year,
                "created_at": movie_obj.created_at,
                "updated_at": movie_obj.updated_at
            }

        except IntegrityError as e:
            logger.error(f"创建电影失败: {e}")
            return {"error": "创建失败，可能包含重复数据"}

    async def get_movie_detail(
        self,
        movie_id: int
    ) -> dict:
        """
        获取电影详情

        Args:
            movie_id: 电影 ID

        Returns:
            dict: 电影详情数据

        Raises:
            Returns {"error": "..."} on failure
        """
        movie = await Movie.get_or_none(id=movie_id)

        if not movie:
            return {"error": f"电影 ID {movie_id} 不存在"}

        return {
            "id": movie.id,
            "name": movie.name,
            "year": movie.year,
            "created_at": movie.created_at,
            "updated_at": movie.updated_at
        }

    async def update_movie(
        self,
        movie_id: int,
        name: Optional[str] = None,
        year: Optional[int] = None
    ) -> dict:
        """
        更新电影

        Args:
            movie_id: 电影 ID
            name: 电影名称（可选）
            year: 上映年份（可选）

        Returns:
            dict: 更新后的电影数据

        Raises:
            Returns {"error": "..."} on failure
        """
        # 构建更新数据
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if year is not None:
            update_data["year"] = year

        if not update_data:
            # 没有更新数据，返回现有电影
            return await self.get_movie_detail(movie_id)

        # 执行更新
        updated_count = await Movie.filter(id=movie_id).update(**update_data)

        if not updated_count:
            return {"error": f"电影 ID {movie_id} 不存在"}

        # 获取更新后的电影
        return await self.get_movie_detail(movie_id)

    async def delete_movie(
        self,
        movie_id: int
    ) -> dict:
        """
        删除电影

        Args:
            movie_id: 电影 ID

        Returns:
            dict: 删除结果

        Raises:
            Returns {"error": "..."} on failure
        """
        deleted_count = await Movie.filter(id=movie_id).delete()

        if not deleted_count:
            return {"error": f"电影 ID {movie_id} 不存在"}

        return {
            "code": 200,
            "msg": "删除成功",
            "deleted_id": movie_id
        }


# 导出服务实例
movie_service = MovieService()

__all__ = ["MovieService", "movie_service"]
