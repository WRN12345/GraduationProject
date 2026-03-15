from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 创建 bookmarks 表
        CREATE TABLE IF NOT EXISTS "bookmarks" (
            "id" SERIAL PRIMARY KEY,
            "user_id" INT NOT NULL REFERENCES "users"(id) ON DELETE CASCADE,
            "post_id" INT NOT NULL REFERENCES "posts"(id) ON DELETE CASCADE,
            "folder" VARCHAR(100) DEFAULT 'default',
            "note" TEXT,
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE("user_id", "post_id")
        );

        -- 创建索引
        CREATE INDEX IF NOT EXISTS "idx_bookmarks_user_id" ON "bookmarks"("user_id");
        CREATE INDEX IF NOT EXISTS "idx_bookmarks_post_id" ON "bookmarks"("post_id");
        CREATE INDEX IF NOT EXISTS "idx_bookmarks_folder" ON "bookmarks"("user_id", "folder");

        -- 添加表注释
        COMMENT ON TABLE "bookmarks" IS '用户收藏帖子记录表';
        COMMENT ON COLUMN "bookmarks"."folder" IS '收藏分类/文件夹';
        COMMENT ON COLUMN "bookmarks"."note" IS '收藏备注';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 删除 bookmarks 表
        DROP TABLE IF EXISTS "bookmarks" CASCADE;
    """
