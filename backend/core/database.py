"""
数据库连接管理工具 - 处理 asyncpg 连接错误
提供重试装饰器、连接健康检查和恢复机制
"""
import asyncio
import logging
from functools import wraps
from typing import TypeVar, ParamSpec, Callable
import asyncpg
from tortoise import connections
from tortoise.exceptions import DBConnectionError, OperationalError

logger = logging.getLogger(__name__)

T = TypeVar('T')
P = ParamSpec('P')


class RetryConfig:
    """重试配置"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        exponential_base: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base


def db_retry(config: RetryConfig = None):
    """
    数据库操作重试装饰器

    自动捕获并重试失败的数据库操作，特别是针对连接错误

    Args:
        config: 重试配置，如果为 None 则使用默认配置

    Example:
        @db_retry()
        async def my_db_operation():
            await SomeModel.filter(id=1).first()
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error = None

            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (
                    asyncpg.exceptions.ConnectionDoesNotExistError,
                    asyncpg.exceptions.InterfaceError,
                    asyncpg.exceptions.PostgresConnectionError,
                    DBConnectionError,
                    OperationalError,
                ) as e:
                    # 这种错误表示表不存在，重试无法解决
                    error_str = str(e).lower()
                    if "relation" in error_str and "does not exist" in error_str:
                        logger.error(
                            f"{func.__name__} 失败: 数据库表不存在 - {str(e)}"
                        )
                        raise
                    last_error = e
                    is_last_attempt = attempt == config.max_attempts - 1

                    if is_last_attempt:
                        logger.error(
                            f"{func.__name__} 在 {config.max_attempts} 次尝试后仍然失败: {str(e)}"
                        )
                        raise

                    # 计算退避延迟（指数退避）
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )

                    logger.warning(
                        f"{func.__name__} 失败 (尝试 {attempt + 1}/{config.max_attempts}): "
                        f"{type(e).__name__}: {str(e)}. "
                        f"{delay:.1f}秒后重试..."
                    )

                    await asyncio.sleep(delay)

            # 理论上不会到达这里，但为了类型检查
            if last_error:
                raise last_error
            raise RuntimeError("重试逻辑异常")

        return wrapper
    return decorator


async def check_db_connection(db_name: str = "default") -> bool:
    """
    检查数据库连接是否正常

    注意：这个函数只检查连接对象是否存在，不执行实际查询。
    实际的连接错误将由 @db_retry() 装饰器处理。

    Args:
        db_name: 数据库连接名称，默认为 "default"

    Returns:
        bool: 连接对象是否存在
    """
    try:
        conn = connections.get(db_name)
        # 只检查连接对象是否存在，不执行查询
        # 避免在检查时触发 ConnectionDoesNotExistError
        return conn is not None
    except Exception as e:
        logger.debug(f"数据库连接检查失败: {type(e).__name__}: {str(e)}")
        return False


async def ensure_connection(db_name: str = "default", max_retries: int = 3):
    """
    确保数据库连接可用，必要时重新连接

    Args:
        db_name: 数据库连接名称
        max_retries: 最大重试次数

    Raises:
        DBConnectionError: 如果无法建立连接
    """
    for attempt in range(max_retries):
        if await check_db_connection(db_name):
            return

        if attempt < max_retries - 1:
            delay = 2.0 ** attempt  # 1s, 2s, 4s
            logger.debug(
                f"数据库连接 '{db_name}' 不存在，{delay:.1f}秒后重试... "
                f"(尝试 {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(delay)

    raise DBConnectionError(f"数据库连接 '{db_name}' 不存在 (已重试 {max_retries} 次)")


async def safe_db_execute(
    query_func: Callable,
    operation_name: str = "数据库操作",
    retry_on_failure: bool = True
):
    """
    安全执行数据库操作的包装函数

    Args:
        query_func: 要执行的数据库操作函数
        operation_name: 操作名称（用于日志）
        retry_on_failure: 失败时是否重试

    Returns:
        查询函数的返回值

    Raises:
        Exception: 如果操作失败且不重试，或重试后仍然失败
    """
    if retry_on_failure:
        return await db_retry()(query_func)()

    # 不重试的情况
    try:
        return await query_func()
    except Exception as e:
        logger.error(f"{operation_name} 失败: {type(e).__name__}: {str(e)}")
        raise


async def get_db_connection_info() -> dict:
    """
    获取当前数据库连接信息（用于调试和监控）

    Returns:
        dict: 包含连接状态信息的字典
    """
    info = {
        "connected": False,
        "database": None,
        "healthy": False
    }

    try:
        conn = connections.get("default")
        if conn:
            info["connected"] = True
            info["database"] = conn.database
            info["healthy"] = await check_db_connection()
    except Exception as e:
        info["error"] = str(e)

    return info
