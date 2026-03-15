"""
@Time : 2025.12.8
@Author: wrn
@Des:
"""

from .login import login
from .user import user, user_public
from .movies import movies
from .posts import router as posts
from .comments import router as comments
from .communities import router as communities
from .votes import router as votes
from .search import router as search
from .bookmarks import router as bookmarks
