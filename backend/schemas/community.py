from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CommunityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class CommunityOut(CommunityCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


