"""
@Created on : 2025/12/8
@Author: wrn
@Des: 用户相关路由
"""

from fastapi import APIRouter, Depends
from backend.models.user import User
from backend.schemas import UserUpdate, User_Pydantic
from backend.core.security import get_current_user, get_password_hash

# 鉴权
user = APIRouter(tags=["用户相关"], dependencies=[Depends(get_current_user)])


# --- 获取当前用户 ---
@user.get("/users", summary="获取当前用户信息", response_model=User_Pydantic)
async def user_info(user_obj: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息
    不需要额外参数，直接通过 Token 解析身份
    """

    return await User_Pydantic.from_tortoise_orm(user_obj)


# --- 更新当前用户 ---
@user.put("/users", summary="更新当前用户信息", response_model=User_Pydantic)
async def user_update(
    user_form: UserUpdate, 
    user_obj: User = Depends(get_current_user) 
):
    """
    更新个人信息
    会自动过滤未传的字段，如果是密码字段会自动加密
    """
    
    update_data = user_form.model_dump(exclude_unset=True)


    if "username" in update_data:
        del update_data["username"]

    if update_data.get("password"):
        update_data["password"] = get_password_hash(update_data["password"])
    elif "password" in update_data:

        del update_data["password"]

  
    if update_data:
        await User.filter(id=user_obj.id).update(**update_data)
        
  
        await user_obj.refresh_from_db()
        

    return await User_Pydantic.from_tortoise_orm(user_obj)


__all__ = [
    "user"
]