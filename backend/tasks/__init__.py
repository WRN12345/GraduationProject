# -*- coding:utf-8 -*-
"""
@Time : 2026.03.15
@Author: wrn
@Des: Background Scheduled Tasks

This module contains all background task triggers that run periodically
to synchronize data between Redis cache and PostgreSQL.
"""

from .tasks import start_background_tasks
from .sync_tasks import start_sync_tasks

__all__ = [
    "start_background_tasks",
    "start_sync_tasks",
]
