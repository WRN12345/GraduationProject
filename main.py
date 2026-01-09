from uvicorn import run
from backend.api import app

# 导出 app 供 uvicorn 使用
__all__ = ["app"]

if __name__ == "__main__":
    run("main:app", host="0.0.0.0", port=8000, reload=True)
