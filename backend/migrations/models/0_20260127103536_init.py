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
COMMENT ON COLUMN "users"."created_at" IS '注册时间';
COMMENT ON COLUMN "users"."last_login" IS '最后登录时间';
CREATE TABLE IF NOT EXISTS "communities" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "description" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "creator_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_communities_name_7969be" ON "communities" ("name");
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
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "search_vector" TSVECTOR NOT NULL,
    "author_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "community_id" INT NOT NULL REFERENCES "communities" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "posts"."hot_rank" IS '热度排名分数';
COMMENT ON COLUMN "posts"."deleted_at" IS '软删除时间戳';
COMMENT ON COLUMN "posts"."is_edited" IS '是否被编辑过';
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
    "PjkVz0OdRretcICzND+3zFdMPP8P92CwQw=="
)
