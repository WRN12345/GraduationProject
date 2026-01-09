-- ================================================================
-- 简化版数据库迁移脚本
-- ================================================================

-- 1. 为 users 表添加新字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS karma INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;

-- 2. 为 posts 表添加新字段
ALTER TABLE posts ADD COLUMN IF NOT EXISTS hot_rank FLOAT DEFAULT 0.0;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS is_edited BOOLEAN DEFAULT FALSE;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 3. 为 comments 表添加新字段
ALTER TABLE comments ADD COLUMN IF NOT EXISTS upvotes INT DEFAULT 0;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS downvotes INT DEFAULT 0;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS score INT DEFAULT 0;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS is_edited BOOLEAN DEFAULT FALSE;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 4. 为 votes 表添加 comment 字段
ALTER TABLE votes ADD COLUMN IF NOT EXISTS comment_id INT REFERENCES comments(id);

-- 5. 创建索引
CREATE INDEX IF NOT EXISTS idx_posts_hot_rank ON posts(hot_rank DESC);
CREATE INDEX IF NOT EXISTS idx_posts_community_hot ON posts(community_id, hot_rank DESC);
CREATE INDEX IF NOT EXISTS idx_posts_deleted_at ON posts(deleted_at) WHERE deleted_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_comments_score ON comments(score DESC);
CREATE INDEX IF NOT EXISTS idx_comments_deleted_at ON comments(deleted_at) WHERE deleted_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_votes_comment ON votes(comment_id);
CREATE INDEX IF NOT EXISTS idx_users_karma ON users(karma DESC);

-- 6. 全文搜索设置（可选，需要 PostgreSQL）
-- CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
-- BEGIN
--     NEW.search_vector :=
--         setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
--         setweight(to_tsvector('english', coalesce(NEW.content, '')), 'B');
--     RETURN NEW;
-- END;
-- $$ LANGUAGE plpgsql;
--
-- DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts;
-- CREATE TRIGGER posts_search_vector_trigger
--     BEFORE INSERT OR UPDATE ON posts
--     FOR EACH ROW
--     EXECUTE FUNCTION posts_search_vector_update();
--
-- CREATE INDEX IF NOT EXISTS idx_posts_search_vector ON posts USING GIN(search_vector);

-- 7. 更新现有数据
UPDATE comments SET score = upvotes - downvotes WHERE score IS NULL OR score = 0;

-- 8. 更新统计信息
ANALYZE users;
ANALYZE posts;
ANALYZE comments;
ANALYZE votes;
