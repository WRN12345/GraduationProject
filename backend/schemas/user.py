"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户 Pydantic 模型 (Schemas)
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from tortoise.contrib.pydantic import pydantic_model_creator
from models.user import User

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
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")

# --- 2.1 用户名修改 (Request Body) ---
class UsernameUpdate(BaseModel):
    """用户名修改请求"""
    username: str = Field(..., description="新用户名", min_length=3, max_length=20)

# --- 2.2 密码修改 (Request Body) ---
class PasswordUpdate(BaseModel):
    """密码修改请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码", min_length=6, max_length=30)

# --- 2.3 用户资料更新扩展 (Request Body) ---
class UserProfileUpdate(BaseModel):
    """用户资料更新请求（包含头像）"""
    nickname: Optional[str] = Field(None, description="昵称")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar: Optional[str] = Field(None, description="头像URL")

# --- 3. 用户简要信息（用于帖子列表等场景） ---
class UserOut(BaseModel):
    """用户简要信息"""
    id: int
    username: str
    nickname: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# --- 4. 公开用户资料 (Response Body) ---
class UserProfile(BaseModel):
    """公开用户资料"""
    id: int
    username: str
    nickname: Optional[str]
    bio: Optional[str]
    avatar: Optional[str] = None
    karma: int
    created_at: datetime
    is_active: bool
    post_count: int = 0
    comment_count: int = 0
    upvote_count: int = 0
    downvote_count: int = 0

    model_config = ConfigDict(from_attributes=True)

# --- 5. 用户活动 (Response Body) ---
class UserActivity(BaseModel):
    """用户活动汇总"""
    posts: list = []
    comments: list = []
    total_posts: int
    total_comments: int


# --- 6. 当前用户信息 (Response Body) ---
class UserInfo(BaseModel):
    """当前登录用户的详细信息（用于 GET /users）"""
    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    karma: int = 0
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# --- 7. 通用响应模型 (Response Body) ---

User_Pydantic = pydantic_model_creator(
    User,
    name="UserReponse", # 给 Swagger 文档显示的名称
    exclude=["password"] # 绝对不能返回密码
)
