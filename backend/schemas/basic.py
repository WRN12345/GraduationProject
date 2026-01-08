from pydantic import BaseModel, Field
from enum import Enum
from typing import Any




class CodeEnum(int, Enum):
    """
    业务状态

    """
    SUCCESS = 200
    ERROR = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    SERVER_ERROR = 500


class ResponseBasic(BaseModel):
    code: CodeEnum = Field( description="状态码",default=CodeEnum.SUCCESS)
    data: Any = Field( description="返回数据",default=None)
    msg: str = Field(description="返回信息",default="成功")


class ResponseSuccess(ResponseBasic):
    code: CodeEnum = Field( description="状态码",default=CodeEnum.SUCCESS)
    data: Any = Field( description="返回数据",default=None)
    msg: str = Field(description="返回信息",default="成功")


class ResponseError(ResponseBasic):
    code: CodeEnum = Field(description="状态码",default=CodeEnum.ERROR)
    data: Any = Field(description="返回数据",default=None)
    msg: str = Field(description="返回信息",default="失败")
    