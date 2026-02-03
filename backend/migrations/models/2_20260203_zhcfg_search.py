from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加 search_vector 字段（如果不存在）
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='posts' AND column_name='search_vector') THEN
                ALTER TABLE "posts" ADD COLUMN "search_vector" TSVECTOR;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='comments' AND column_name='search_vector') THEN
                ALTER TABLE "comments" ADD COLUMN "search_vector" TSVECTOR;
            END IF;
        END $$;

        -- 创建中文全文搜索配置
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'zhcfg') THEN
                CREATE TEXT SEARCH CONFIGURATION zhcfg (PARSER = zhparser);
            END IF;
        END $$;

        -- 更新帖子搜索向量为 zhcfg 配置
        CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('zhcfg', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('zhcfg', COALESCE(NEW.content, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- 重建所有帖子的搜索向量
        UPDATE posts
        SET search_vector =
            setweight(to_tsvector('zhcfg', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('zhcfg', COALESCE(content, '')), 'B');

        -- 更新评论搜索向量为 zhcfg 配置
        CREATE OR REPLACE FUNCTION comments_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('zhcfg', COALESCE(NEW.content, '')), 'A');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- 重建所有评论的搜索向量
        UPDATE comments
        SET search_vector = to_tsvector('zhcfg', COALESCE(content, ''));

        -- 确保触发器存在并重新绑定
        DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts;
        CREATE TRIGGER posts_search_vector_trigger
            BEFORE INSERT OR UPDATE ON posts
            FOR EACH ROW
            EXECUTE FUNCTION posts_search_vector_update();

        DROP TRIGGER IF EXISTS comments_search_vector_trigger ON comments;
        CREATE TRIGGER comments_search_vector_trigger
            BEFORE INSERT OR UPDATE ON comments
            FOR EACH ROW
            EXECUTE FUNCTION comments_search_vector_update();

        -- 创建 GIN 索引
        CREATE INDEX IF NOT EXISTS idx_posts_search_vector ON posts USING GIN (search_vector);
        CREATE INDEX IF NOT EXISTS idx_comments_search_vector ON comments USING GIN (search_vector);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts;
        DROP TRIGGER IF EXISTS comments_search_vector_trigger ON comments;
        DROP FUNCTION IF EXISTS posts_search_vector_update();
        DROP FUNCTION IF EXISTS comments_search_vector_update();
        DROP INDEX IF EXISTS idx_posts_search_vector;
        DROP INDEX IF EXISTS idx_comments_search_vector;
        ALTER TABLE "posts" DROP COLUMN IF EXISTS "search_vector";
        ALTER TABLE "comments" DROP COLUMN IF EXISTS "search_vector";
    """


MODELS_STATE = (
    "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"
)
