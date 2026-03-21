from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(255) NOT NULL,
    "nickname" VARCHAR(50) DEFAULT '新用户',
    "email" VARCHAR(100) UNIQUE,
    "is_active" BOOL NOT NULL DEFAULT True,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "karma" INT NOT NULL DEFAULT 0,
    "bio" TEXT,
    "avatar" VARCHAR(500),
    "post_count" INT NOT NULL DEFAULT 0,
    "comment_count" INT NOT NULL DEFAULT 0,
    "last_active_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_login" TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
COMMENT ON COLUMN "users"."username" IS '账户';
COMMENT ON COLUMN "users"."password" IS '密码(Hash)';
COMMENT ON COLUMN "users"."nickname" IS '昵称';
COMMENT ON COLUMN "users"."email" IS '邮箱';
COMMENT ON COLUMN "users"."is_active" IS '是否激活/冻结';
COMMENT ON COLUMN "users"."is_superuser" IS '是否管理员';
COMMENT ON COLUMN "users"."karma" IS '声望值（来自帖子和评论的点赞）';
COMMENT ON COLUMN "users"."bio" IS '个人简介';
COMMENT ON COLUMN "users"."avatar" IS '头像URL';
COMMENT ON COLUMN "users"."post_count" IS '发帖数量';
COMMENT ON COLUMN "users"."comment_count" IS '评论数量';
COMMENT ON COLUMN "users"."last_active_at" IS '最后活跃时间';
COMMENT ON COLUMN "users"."created_at" IS '注册时间';
COMMENT ON COLUMN "users"."last_login" IS '最后登录时间';
CREATE TABLE IF NOT EXISTS "communities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" TEXT,
    "member_count" INT NOT NULL DEFAULT 0,
    "post_count" INT NOT NULL DEFAULT 0,
    "last_active_at" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_communities_name_7969be" ON "communities" ("name");
COMMENT ON COLUMN "communities"."member_count" IS '成员数量';
COMMENT ON COLUMN "communities"."post_count" IS '帖子数量';
COMMENT ON COLUMN "communities"."last_active_at" IS '最后活跃时间';
COMMENT ON TABLE "communities" IS '板块 / Subreddit';
CREATE TABLE IF NOT EXISTS "posts" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "content" TEXT,
    "upvotes" INT NOT NULL DEFAULT 0,
    "downvotes" INT NOT NULL DEFAULT 0,
    "score" INT NOT NULL DEFAULT 0,
    "hot_rank" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "deleted_at" TIMESTAMPTZ,
    "is_edited" BOOL NOT NULL DEFAULT False,
    "is_locked" BOOL NOT NULL DEFAULT False,
    "is_highlighted" BOOL NOT NULL DEFAULT False,
    "is_pinned" BOOL NOT NULL DEFAULT False,
    "deleted_by_id" INT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "community_id" INT NOT NULL REFERENCES "communities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "posts"."hot_rank" IS '热度排名分数';
COMMENT ON COLUMN "posts"."deleted_at" IS '软删除时间戳';
COMMENT ON COLUMN "posts"."is_edited" IS '是否被编辑过';
COMMENT ON COLUMN "posts"."is_locked" IS '禁止新增评论';
COMMENT ON COLUMN "posts"."is_highlighted" IS '精华内容';
COMMENT ON COLUMN "posts"."is_pinned" IS '置顶帖子';
COMMENT ON COLUMN "posts"."deleted_by_id" IS '谁删除了该帖子';
COMMENT ON TABLE "posts" IS '帖子';
CREATE TABLE IF NOT EXISTS "comments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "content" TEXT NOT NULL,
    "upvotes" INT NOT NULL DEFAULT 0,
    "downvotes" INT NOT NULL DEFAULT 0,
    "score" INT NOT NULL DEFAULT 0,
    "deleted_at" TIMESTAMPTZ,
    "is_edited" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "author_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "parent_id" INT REFERENCES "comments" ("id") ON DELETE CASCADE,
    "post_id" INT NOT NULL REFERENCES "posts" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "comments"."deleted_at" IS '软删除时间戳';
COMMENT ON COLUMN "comments"."is_edited" IS '是否被编辑过';
COMMENT ON TABLE "comments" IS '评论 (无限层级)';
CREATE TABLE IF NOT EXISTS "votes" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "direction" INT NOT NULL,
    "comment_id" INT REFERENCES "comments" ("id") ON DELETE CASCADE,
    "post_id" INT REFERENCES "posts" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON TABLE "votes" IS '投票记录 - 支持帖子和评论';
CREATE TABLE IF NOT EXISTS "post_attachments" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "attachment_type" VARCHAR(10) NOT NULL,
    "file_name" VARCHAR(255) NOT NULL,
    "file_url" VARCHAR(1024) NOT NULL,
    "file_size" BIGINT NOT NULL,
    "mime_type" VARCHAR(100) NOT NULL,
    "sort_order" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "post_id" INT REFERENCES "posts" ("id") ON DELETE CASCADE,
    "uploader_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
COMMENT ON COLUMN "post_attachments"."attachment_type" IS 'IMAGE: image\nVIDEO: video\nFILE: file';
COMMENT ON TABLE "post_attachments" IS '帖子附件';
CREATE TABLE IF NOT EXISTS "community_memberships" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "role" INT NOT NULL DEFAULT 0,
    "joined_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "community_id" INT NOT NULL REFERENCES "communities" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_community_m_user_id_b71652" UNIQUE ("user_id", "community_id")
);
COMMENT ON COLUMN "community_memberships"."role" IS '角色: -1=黑名单, 0=成员, 1=管理员, 2=群主';
COMMENT ON COLUMN "community_memberships"."joined_at" IS '加入时间';
COMMENT ON COLUMN "community_memberships"."updated_at" IS '更新时间';
COMMENT ON TABLE "community_memberships" IS '社区成员关系 - Many-to-Many between User and Community';
CREATE TABLE IF NOT EXISTS "bookmarks" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "folder" VARCHAR(100) DEFAULT 'default',
    "note" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL,
    "post_id" INT NOT NULL REFERENCES "posts" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_bookmarks_user_id_0cbe5c" UNIQUE ("user_id", "post_id")
);
COMMENT ON TABLE "bookmarks" IS '收藏模型 - 用户收藏帖子';
CREATE TABLE IF NOT EXISTS "audit_logs" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "target_type" INT NOT NULL,
    "target_id" INT NOT NULL,
    "action_type" INT NOT NULL,
    "reason" TEXT,
    "metadata" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "actor_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_audit_logs_actor_i_6fa712" ON "audit_logs" ("actor_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_audit_logs_target__f7a138" ON "audit_logs" ("target_type", "target_id", "created_at");
CREATE INDEX IF NOT EXISTS "idx_audit_logs_action__bb25a2" ON "audit_logs" ("action_type", "created_at");
COMMENT ON COLUMN "audit_logs"."target_type" IS '目标类型';
COMMENT ON COLUMN "audit_logs"."target_id" IS '目标ID';
COMMENT ON COLUMN "audit_logs"."action_type" IS '操作类型';
COMMENT ON COLUMN "audit_logs"."reason" IS '操作原因';
COMMENT ON COLUMN "audit_logs"."metadata" IS '额外上下文信息';
COMMENT ON COLUMN "audit_logs"."created_at" IS '操作时间';
COMMENT ON TABLE "audit_logs" IS '审计日志 - 记录所有管理操作';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "4GlrpmtqUq5zevn5f8/0ru4="
)
