from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加 search_vector 列用于全文搜索
        ALTER TABLE "posts" ADD COLUMN IF NOT EXISTS "search_vector" tsvector;

        -- 创建 GIN 索引加速全文搜索
        CREATE INDEX IF NOT EXISTS "idx_posts_search_vector" ON "posts" USING gin ("search_vector");

        -- 创建 zhparser 全文搜索配置（如果不存在）
        CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS "zhcfg" (PARSER zhparser);

        -- 配置中文分词词典
        ALTER TEXT SEARCH CONFIGURATION "zhcfg" ADD MAPPING FOR n,v,a,i,e,l WITH simple;

        -- 创建更新搜索向量的函数（使用 zhparser 中文分词）
        CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector :=
                setweight(to_tsvector('zhcfg', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('zhcfg', COALESCE(NEW.content, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        -- 创建触发器在插入/更新时自动更新搜索向量
        DROP TRIGGER IF EXISTS "posts_search_vector_trigger" ON "posts";
        CREATE TRIGGER "posts_search_vector_trigger"
            BEFORE INSERT OR UPDATE ON "posts"
            FOR EACH ROW
            EXECUTE FUNCTION posts_search_vector_update();

        -- 为现有数据生成搜索向量
        UPDATE "posts" SET "search_vector" =
            setweight(to_tsvector('zhcfg', COALESCE("title", '')), 'A') ||
            setweight(to_tsvector('zhcfg', COALESCE("content", '')), 'B')
        WHERE "search_vector" IS NULL;
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TRIGGER IF EXISTS "posts_search_vector_trigger" ON "posts";
        DROP FUNCTION IF EXISTS posts_search_vector_update();
        DROP INDEX IF EXISTS "idx_posts_search_vector";
        ALTER TABLE "posts" DROP COLUMN IF EXISTS "search_vector";
    """


MODELS_STATE = (
    "eJztXWtzm8gS/SuUPmWrnCxC4qHU3Vsl20riXT9SfuRubZxSDTDIXCPQ8ojju5X/fqcHiT"
    "cY9ABk8SGKPEwjONMz09N9puef3txSseG8u3Ow3XvP/NMz0RyTL7HyI6aHFouwFApcJBu0"
    "okdq0BIkO66NFJcUashwMClSsaPY+sLVLZOUmp5hQKGlkIq6OQuLPFP/28NT15ph94E+yN"
    "dvpFg3VfwDO6s/F49TTceGGntOXYXfpuVT93lBy85M9wOtCL8mTxXL8OZmWHnx7D5YZlBb"
    "N10onWET28jFcHvX9uDx4emWr7l6I/9Jwyr+I0ZkVKwhz3Ajr1sSA8UyAT/yNA59wRn8yl"
    "uuPxSH0kAYSqQKfZKgRPzpv1747r4gReDytveTXkcu8mtQGEPcoNno9xR6Jw/IzoYvKpMA"
    "kTx6EsQVZDtAsXfvSSon3HsCNxB75fCcox9TA5sz94H8ybMF4H0ZX598Gl+/4dlf4N4WUW"
    "pf1S+XVzh6CfAN8Vwgx3my7AxtzMczKrMdPFcFIaBhV3wJUV5WCKKixPbffELOwy/r4Mrx"
    "AlgSa1cZOm1OLSmrjxWVdWozFrQLhWxErIERIGXWQIiz0kR5UwiLQgDnlQaaWw7dBfPkW"
    "5UQTcQ2Aq06w8CIxZhAqQs99cBss+WQZLUyoWSXotjqTtTMgfq3zO09diyDIzMnKkpKpeA"
    "VSaCuxoNAqxTOsppZEwY0lFWU4hSC+pA/pUU9WWZYI7VQTnMCyA+vro6h5vMHedvgxac3Sa"
    "gvrs4npA2oC1AKukujk5vMdgdb4Ftb2mvVEM+Jloj+Nl2UgJ9UUZ98jlkBSjhpTbB/ojsOa"
    "pggAX1X7bBtoUxmznXSRpotNgnqsyzA+Xe0zQWhmxRICOz1MeIlOM+IC7zLOAukTqSrAz"
    "hUyZXRUEi30VWHoEtwmN6h1HJYWgrtl3YCrJupdvgFv/IaYRl9dqmxbzRe4g5BJ8UTlli4b"
    "sib6zet5M/b2PqvRqv31yM/6QaPX9eXjm/uvy4qh7R/pPzq+MExOg7MaQzRpb8OTKUaBx"
    "ofjQYgp4r2t31+XomRzmbo8joSFvMluMSvDy/65ccQOJCTY8iA7W/GicEXiQKPOorWjNjg"
    "GLN59isDmhKrmFMo2Ns05gaiCibb5VNUQaopwQQV5/jbGTT0glo1aX4u9WXmocFQWTp1MZi"
    "37iDiUwZAOwaUegRrw03H4vPLiY3t+OLz7EB+XR8O4ErXGwwXpW+ERKjSHAT5j9nt58Y+J"
    "P56+pyQiEl48HMpr8Y1rv9qwfPhDzXmprW0xSpUWBWxauieDeyMYC/RnPHJbfQ1Ftd3AsKl"
    "sB2BzOmavv2yJupV6bxvNS/PWnvZVcpbG7aRw1rpptr9e5AssU9WxREMHI1nj+8ng1eY+0x"
    "4v+EAhkpj0/IVqexK6FOfLdc7GSsIZdiH/64xgaiWKcbfuk1/0JuUWsPL+1W/rnS41Vp2KdT"
    "tsSGIJz4d9lnHJZDOuBBns3VN9WLk+WNnvcYFOiXG8LwmdxijxHwFoaFVDrVu0h52EJXAUDG"
    "wc3qnCy2i8wcz2VsOw/6Ylsd5SK44x4rjGxZj3NkP24IyvHyNnuMBPJUnZpNG0IxhvucW7M"
    "9gwLMD4uz8gyS9KU5N0+WIBPN6FPDb8MvRW2OjAj+yhbJj+AHBs+LEXwwLbkRjV0JEl2ls75"
    "pybxlwLoEp7UwYPvFztOk7bm9u3Y8gtp5BKpuY2XVWUvCF5Opz9/UBiDTDr==="
)
