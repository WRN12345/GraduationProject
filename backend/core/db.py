"""
@Created on : 2026.2.4
@Author: wrn
@Des: 数据库连接管理服务 - 读写分离
"""
from typing import Optional
from tortoise import connections
from backend.core.config import settings


class DatabaseService:
    """数据库服务 - 管理读写分离连接"""

    @staticmethod
    def get_read_connection(force_master: bool = False):
        """
        获取读连接

        Args:
            force_master: 是否强制读主库

        Returns:
            数据库连接对象
        """
        if force_master or settings.DB_READ_FROM_MASTER:
            return connections.get("master")
        return connections.get("replica")

    @staticmethod
    def get_write_connection():
        """获取写连接 (主库)"""
        return connections.get("master")

    @staticmethod
    async def execute_read_query(
        sql: str,
        params: Optional[list] = None,
        force_master: bool = False
    ):
        """
        执行读查询 (使用从库)

        Args:
            sql: SQL 查询语句
            params: 查询参数
            force_master: 是否强制读主库

        Returns:
            查询结果字典列表
        """
        conn = DatabaseService.get_read_connection(force_master)
        return await conn.execute_query_dict(sql, params or [])

    @staticmethod
    async def execute_write_query(sql: str, params: Optional[list] = None):
        """
        执行写查询 (使用主库)

        Args:
            sql: SQL 写语句
            params: 查询参数

        Returns:
            执行结果
        """
        conn = DatabaseService.get_write_connection()
        return await conn.execute_query_dict(sql, params or [])


# 导出服务实例
db_service = DatabaseService()

__all__ = ["db_service", "DatabaseService"]
