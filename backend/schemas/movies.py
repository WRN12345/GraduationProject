"""
@Created on : 2025/12/8
@Author: wrn
@Des: 电影 Pydantic 模型 (Schemas)
"""

from typing import Optional
from pydantic import BaseModel, Field
from tortoise.contrib.pydantic import pydantic_model_creator
from models.movies import Movie 

# --- 新增电影 ---
class MovieCreate(BaseModel):
    """
    用于创建接口，字段通常为必填
    """
    name: str = Field(..., max_length=50, description="电影名称")
    year: int = Field(..., ge=1888, description="年份")

# --- 更新电影---
class MovieUpdate(BaseModel):
    """
    用于更新接口，所有字段均为选填 (Optional)
    """
    name: Optional[str] = Field(None, max_length=50, description="电影名称")
    year: Optional[int] = Field(None, ge=1888, description="年份")

# --- 响应模型 ---
Movie_Pydantic = pydantic_model_creator(
    Movie, 
    name="MovieResponse" 
)