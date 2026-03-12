from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD COLUMN "avatar" VARCHAR(500);
        COMMENT ON COLUMN "users"."avatar" IS '头像URL';
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN IF EXISTS "avatar";
    """
