from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加 search_vector 字段到 comments 表
        ALTER TABLE "comments" ADD COLUMN "search_vector" TSVECTOR;

        -- 为现有评论更新 search_vector（内容）
        UPDATE "comments" SET "search_vector" = to_tsvector('english', COALESCE(content, ''));

        -- 设置 search_vector 为 NOT NULL
        ALTER TABLE "comments" ALTER COLUMN "search_vector" SET NOT NULL;

        -- 为 posts 表创建 GIN 索引（加速全文搜索）
        CREATE INDEX IF NOT EXISTS "idx_posts_search_vector" ON "posts" USING GIN ("search_vector");

        -- 为 comments 表创建 GIN 索引（加速全文搜索）
        CREATE INDEX IF NOT EXISTS "idx_comments_search_vector" ON "comments" USING GIN ("search_vector");

        -- 为 posts 表创建自动更新触发器
        CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW."search_vector" :=
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS posts_search_vector_trigger ON "posts";
        CREATE TRIGGER posts_search_vector_trigger
            BEFORE INSERT OR UPDATE ON "posts"
            FOR EACH ROW
            EXECUTE FUNCTION posts_search_vector_update();

        -- 为 comments 表创建自动更新触发器
        CREATE OR REPLACE FUNCTION comments_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW."search_vector" :=
                setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'A');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS comments_search_vector_trigger ON "comments";
        CREATE TRIGGER comments_search_vector_trigger
            BEFORE INSERT OR UPDATE ON "comments"
            FOR EACH ROW
            EXECUTE FUNCTION comments_search_vector_update();
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 删除触发器
        DROP TRIGGER IF EXISTS posts_search_vector_trigger ON "posts";
        DROP TRIGGER IF EXISTS comments_search_vector_trigger ON "comments";

        -- 删除触发器函数
        DROP FUNCTION IF EXISTS posts_search_vector_update();
        DROP FUNCTION IF EXISTS comments_search_vector_update();

        -- 删除索引
        DROP INDEX IF EXISTS "idx_posts_search_vector";
        DROP INDEX IF EXISTS "idx_comments_search_vector";

        -- 删除 search_vector 列
        ALTER TABLE "comments" DROP COLUMN IF EXISTS "search_vector";
        """


MODELS_STATE = (
    "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"
    "Ea56dXIqnoc6jm5b4QCnaX5ume/ieP4fy3sSwA=="
)
