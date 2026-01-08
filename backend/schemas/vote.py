from pydantic import BaseModel

# --- Vote ---
class VoteCreate(BaseModel):
    post_id: int
    dir: int # 1 for up, -1 for down, 0 for clear