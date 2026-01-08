"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户 Pydantic 模型 (Schemas)
"""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from tortoise.contrib.pydantic import pydantic_model_creator
from backend.models.user import User

# --- 1. 注册/创建用户模型 (Request Body) ---
class UserCreate(BaseModel):
    """
    用于注册接口，所有字段均为必填
    """
    username: str = Field(..., description="用户名", min_length=3, max_length=20)
    password: str = Field(..., description="密码", min_length=6, max_length=30)
    nickname: Optional[str] = Field(default=None, description="昵称")
    email: Optional[EmailStr] = Field(default=None, description="邮箱")

# --- 2. 更新用户模型 (Request Body) ---
class UserUpdate(BaseModel):
    """
    用于更新接口，所有字段均为选填 (Optional)
    用户可能只改昵称，不改密码
    """
    password: Optional[str] = Field(None, description="新密码", min_length=6, max_length=30)
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    

# --- 3. 响应模型 (Response Body) ---

User_Pydantic = pydantic_model_creator(
    User, 
    name="UserReponse", # 给 Swagger 文档显示的名称
    exclude=["password"] # 绝对不能返回密码
)
