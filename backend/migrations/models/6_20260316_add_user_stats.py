from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "post_count" INT NOT NULL DEFAULT 0;
        COMMENT ON COLUMN "users"."post_count" IS '发帖数量';

        ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "comment_count" INT NOT NULL DEFAULT 0;
        COMMENT ON COLUMN "users"."comment_count" IS '评论数量';

        ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "last_active_at" TIMESTAMPTZ;
        COMMENT ON COLUMN "users"."last_active_at" IS '最后活跃时间';

        CREATE INDEX IF NOT EXISTS "idx_user_post_count" ON "users"("post_count" DESC);
        CREATE INDEX IF NOT EXISTS "idx_user_comment_count" ON "users"("comment_count" DESC);
        CREATE INDEX IF NOT EXISTS "idx_user_last_active" ON "users"("last_active_at" DESC);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_user_last_active";
        DROP INDEX IF EXISTS "idx_user_comment_count";
        DROP INDEX IF EXISTS "idx_user_post_count";

        ALTER TABLE "users" DROP COLUMN IF EXISTS "last_active_at";
        ALTER TABLE "users" DROP COLUMN IF EXISTS "comment_count";
        ALTER TABLE "users" DROP COLUMN IF EXISTS "post_count";
    """
