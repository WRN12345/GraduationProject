"""
@Time : 2025.12.8
@Author: wrn
@Des: 导包
"""
from fastapi import APIRouter
from .endpoints import memberships
from .endpoints import *
from .endpoints import uploads
from .endpoints import attachments
from .endpoints import hot



v1 = APIRouter(prefix="/v1")

v1.include_router(login)
v1.include_router(user)
v1.include_router(user_public)
v1.include_router(posts)
v1.include_router(comments)
v1.include_router(communities)
v1.include_router(votes)
v1.include_router(search)
v1.include_router(bookmarks)
v1.include_router(memberships.router)
v1.include_router(uploads.router)
v1.include_router(attachments.router)
v1.include_router(hot.router)
