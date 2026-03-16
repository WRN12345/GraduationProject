from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "communities" ADD COLUMN IF NOT EXISTS "post_count" INT NOT NULL DEFAULT 0;
        COMMENT ON COLUMN "communities"."post_count" IS '帖子数量';

        ALTER TABLE "communities" ADD COLUMN IF NOT EXISTS "last_active_at" TIMESTAMPTZ;
        COMMENT ON COLUMN "communities"."last_active_at" IS '最后活跃时间';

        CREATE INDEX IF NOT EXISTS "idx_community_post_count" ON "communities"("post_count" DESC);
        CREATE INDEX IF NOT EXISTS "idx_community_last_active" ON "communities"("last_active_at" DESC);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "idx_community_last_active";
        DROP INDEX IF EXISTS "idx_community_post_count";

        ALTER TABLE "communities" DROP COLUMN IF EXISTS "last_active_at";
        ALTER TABLE "communities" DROP COLUMN IF EXISTS "post_count";
    """
