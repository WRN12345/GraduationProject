from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加 search_vector 列用于用户全文搜索
        ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "search_vector" tsvector;

        -- 创建 GIN 索引加速全文搜索
        CREATE INDEX IF NOT EXISTS "idx_users_search_vector" ON "users" USING gin ("search_vector");

        -- 创建更新搜索向量的函数（使用 zhparser 中文分词）
        CREATE OR REPLACE FUNCTION users_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('zhcfg', COALESCE(NEW.username, '')), 'A') ||
                setweight(to_tsvector('zhcfg', COALESCE(NEW.nickname, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- 创建触发器在插入/更新时自动更新搜索向量
        DROP TRIGGER IF EXISTS "users_search_vector_trigger" ON "users";
        CREATE TRIGGER "users_search_vector_trigger"
            BEFORE INSERT OR UPDATE ON "users"
            FOR EACH ROW
            EXECUTE FUNCTION users_search_vector_update();

        -- 为现有数据生成搜索向量
        UPDATE "users" SET "search_vector" =
            setweight(to_tsvector('zhcfg', COALESCE("username", '')), 'A') ||
            setweight(to_tsvector('zhcfg', COALESCE("nickname", '')), 'B')
        WHERE "search_vector" IS NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS "users_search_vector_trigger" ON "users";
        DROP FUNCTION IF EXISTS users_search_vector_update();
        DROP INDEX IF EXISTS "idx_users_search_vector";
        ALTER TABLE "users" DROP COLUMN IF EXISTS "search_vector";
    """
