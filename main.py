from uvicorn import run
from backend.api import app

from backend.api.v1.endpoints import comments, votes ,communities, posts

# 1. 注册路由
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
app.include_router(votes.router, prefix="/api/v1/votes", tags=["Votes"])
app.include_router(communities.router, prefix="/api/v1/communities", tags=["Communities"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000 ,reload=True)