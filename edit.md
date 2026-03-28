修改.env的管理员key
在前端做用户登出删除refresh/access token
前端聚合搜索用户和帖子 -->

<热搜帖子使用redis热度算法，zset排序，不直接接触pgsql，
搜索使用倒排索引，添加zhparser“中文全文搜索”   PostgreSQL 数据库的扩展插件，1. 核心作用：中文分词（Word Segmentation）
这是 zhparser 最核心的功能。
英文搜索简单：英文单词之间有空格。比如搜索 "I love coding"，数据库很容易切分成 "I"、"love"、"coding"。
中文搜索困难：中文句子是连在一起的，比如“我爱编写代码”。数据库如果不分词，就不知道你要搜的是“编写”还是“代码”。 


主库 (5432)：负责所有的发帖、评论、修改用户信息。
从库 (5433)：负责你的 zhparser 全文检索、帖子列表展示。 -->
 基于 PostgreSQL 流复制的读写分离架构”、“GIN 倒排索引异步查询优化”、“多级缓存策略” 

读写分离的一个“大坑”：主从延迟（毕设需注意）
这是读写分离架构中必然存在的问题，你在写毕设论文时可以作为**“架构难点分析”**写进去：
现象：用户点击“发布帖子”后，页面重定向到“帖子列表”。由于主库同步到从库有几十毫秒的延迟，用户可能在列表页刷不出刚才发的帖子，导致用户以为发帖失败。
对策（毕设建议）：
重要读取走主库：涉及到个人中心、刚发布后的跳转，手动用 .using_db("default") 强行读主库。
非即时读取走从库：首页列表、搜索、排行榜等对实时性要求没那么高的，全部走从库。 

 用一个URL,PGSQL里面自动路由到对应的从库主库

本系统在底层构建了基于 PostgreSQL 流复制 的主从架构，并引入 Pgpool-II 作为中间件实现了透明化的读写分离与负载均衡。该架构有效地解决了高并发全文搜索对主库产生的 I/O 冲击，确保了系统的写入可用性与查询响应速度，达到了工业级应用的标准

物理读写分离：后端代码只需要连 9999 端口，写操作自动去 5432，读操作自动去 5433。
负载均衡：如果你以后加了 Slave 2、Slave 3，Pgpool 会自动把查询平分给它们。
高安全性：通过 MD5 认证和权限控制。
高性能搜索支持：你的 zhparser 全文检索现在完全在 standby 节点运行，哪怕搜索压力再大，也不会卡死主库的发帖功能。

“本系统采用基于中间件的透明路由策略，有效地屏蔽了底层数据库集群的复杂拓扑，降低了上层业务代码的耦合度。”
“通过配置细粒度的权重分配（Weighting Factor），实现了读流量在三个从节点间的均匀分布（Round Robin/Random），显著提升了系统的并发查询吞吐量（Throughput）。”
“在运维层面，针对 Pgpool 状态持久化机制导致的节点状态不同步问题，设计了基于 PCP 协议的节点动态挂载方案，确保了故障恢复后的快速上线。”
“结合 PostgreSQL 的 WAL（Write-Ahead Logging）机制 与 Pgpool 的连接池技术，不仅保证了数据的高可靠性，还通过复用数据库连接大幅减少了 TCP 握手开销。”


根本原因：Pgpool 查询缓存权限问题
1. 问题链条

Pgpool 尝试使用查询缓存功能
    ↓
需要创建锁文件：/var/log/postgresql/memq_lock_file
    ↓
目录权限不足（虽然目录存在，但锁文件所有者是 root）
    ↓
锁文件创建失败，查询执行异常
    ↓
连接状态变得不稳定
    ↓
后续操作使用该连接时出现 ConnectionDoesNotExistError
2. 具体原因
权限冲突：

Pgpool 进程以 postgres 用户运行
锁文件 /var/log/postgresql/memq_lock_file 的所有者是 root
postgres 用户无法覆盖 root 拥有的文件
为什么会有这个文件：

之前可能有 root 进程创建了这个文件
或者是之前手动创建的，权限设置不当
3. 修复方案
关键步骤：

删除旧的锁文件：rm -f /var/log/postgresql/memq_lock_file
确保 /var/log/postgresql 目录权限正确：chmod 777 + chown postgres:postgres
重新加载 Pgpool 配置
为什么这样修复有效：

删除旧文件后，Pgpool 可以重新创建属于自己的锁文件
目录权限设置为 777 确保 postgres 用户可以写入
Pgpool 重新创建锁文件后，查询缓存功能正常工作
为什么重试机制不够
重试机制（@db_retry() 装饰器）只是应对症状，而不是解决根本问题：

重试可以在连接失败时自动重试
但如果 Pgpool 本身配置有问题，重试也会失败
只有修复了 Pgpool 的权限问题，重试机制才能真正发挥作用
修复后的效果
✅ 之前：频繁出现连接错误，需要不断重试
✅ 之后：连接稳定，无需频繁重试

总结
数据库连接不成功的根本原因是：

Pgpool 的查询缓存功能需要创建锁文件 /var/log/postgresql/memq_lock_file，但由于该文件权限不当（root 拥有），导致 Pgpool（以 postgres 用户运行）无法覆盖，进而导致查询缓存功能失败，最终引发连接异常。

解决方案：删除旧锁文件，让 Pgpool 重新创建，并确保目录权限正确。

Vue 3.5.25 + Composition API
Pinia 2.3.1 - 状态管理
Element Plus 2.12.0 - UI 组件
openapi-fetch 0.15.0 - 类型安全 API 调用
lucide-vue-next - 图标库

【任务背景】
我正在用 Vue3 开发一个前端项目，里面有一个 FileUploader.vue 组件用于上传图片到 MinIO。
【Bug 现象】
现在遇到了一个经典的 Bug：我只选择上传了一张图片，但页面（图片列表）上却显示了两张一模一样的图。并且提示“已选择 2 个附件”。
【Bug 原因分析】
我排查过 Network 面板，原因是：
选择文件后，前端通过 URL.createObjectURL 生成了一个 blob: 的本地预览图，并 push 到了附件数组里。
文件上传到 MinIO 成功后，后端返回了一个真实的网络地址（带有时间戳的新文件名）。
前端拿到这个真实的 URL 后，没有去替换刚才的本地预览图对象，而是又 push 了一次到附件数组里。导致本地图和线上图同时存在。
【修改诉求】
请帮我修改下面这段上传逻辑的代码。
核心要求：在上传成功后，通过某种唯一标识（比如临时 ID、uid 或 file 对象本身）找到原先那个本地预览图对应的数组项，把它的 url 替换为后端返回的真实 url，并更新其上传状态，绝对不能再 Push 新的对象进去。
问题根源
选择文件时，Element UI 自动在 internalFileList 中添加一个带有本地 blob: 预览图的对象
上传成功后，代码又 push 了一个新对象到数组，导致本地预览图和线上真实图同时存在
修复方案
核心思路：通过 uid 唯一标识找到原文件对象，更新其属性而非添加新对象

修改点：
添加文件映射（第109行）


const fileMap = new Map()
记录文件 uid（handleChange 方法）

在文件状态改变时记录 uid 到原始文件的映射
修改 customRequest 方法（第201-251行）

通过 file.uid 在 internalFileList 中查找对应对象
直接更新该对象的 url、attachmentId、status 等属性
不再 push 新对象
修改 handleSuccess 方法（第276-311行）

同样通过 uid 查找并更新对象
不再 push 新对象

户点击登出 → 前端调用 /v1/logout → 后端将 Token 加入 Redis 黑名单 → 前端清除本地 Token
后续请求 → 后端检查 Token 是否在黑名单 → 是则返回 401

 Python 基础与进阶语法
面向对象编程 (OOP)：使用了类 TokenBlacklistService 封装功能，体现了高内聚低耦合的原则。
单例模式 (Singleton)：在文件末尾通过 token_blacklist_service = TokenBlacklistService() 实例化，并在全局复用，确保整个应用共享同一个连接池，节省内存。
类型注解 (Type Hinting)：使用了 Optional, str, dict, bool 等注解。这增强了代码的可读性和 IDE 的补全功能，体现了你对现代 Python 语法的掌握。
异常处理 (Exception Handling)：使用了细致的 try...except 结构，捕获了 JWT 特定的错误（ExpiredSignatureError, InvalidTokenError）和通用的 Exception，保证了系统的健壮性。
2. 异步编程 (Asynchronous Programming)
async/await：使用了 redis.asyncio，这意味着代码是非阻塞的。在社区论坛这种高并发场景下，异步处理 Redis IO 操作可以极大提升服务器的吞吐量。
3. 安全与 Web 开发相关
JWT (JSON Web Token)：
解析与验证：使用 jwt.decode 验证签名（verify_signature=True），确保 Token 不是伪造的。
过期处理：通过获取 exp 字段计算剩余寿命（TTL）。
黑名单机制：解决了 JWT 状态不可控的弊端（JWT 一旦签发，在到期前默认始终有效）。通过 Redis 记录已登出的 Token，实现真正安全的强制退出。
4. Redis 数据库应用
TTL (Time To Live)：使用了 setex (Set with Expiration)。这是核心亮点：黑名单记录的寿命与 Token 剩余寿命一致。这样 Redis 不会无限膨胀，到期自动清理，非常节省内存。

异步非阻塞 ORM 操作 (async/await)
知识点：使用了异步 ORM 对数据库进行增删改查。相比传统的同步框架（如 Django/Flask 默认模式），异步 ORM 能极大提高论坛在高并发情况下的吞吐量。
规避 N+1 查询问题 (prefetch_related)
知识点：在 get_user_posts 和 get_user_comments 中，你使用了 .prefetch_related('author', 'community')。
答辩话术：“为了避免在循环列表中每次都去数据库查询作者和社区信息（即臭名昭著的 N+1 查询性能瓶颈），我使用了预加载机制，用一次 SQL JOIN/IN 查询就将关联数据提取到内存中，极大提升了接口响应速度。”
密码安全与哈希校验
知识点：在 update_password 中，密码没有明文比对，而是借助底层的 get_password_hash 和 verify_password（通常基于 bcrypt 算法）来保证数据库泄露也不会导致用户密码失窃。
云原生/微服务化存储思想
知识点：头像上传没有保存在本地磁盘，而是调用了 rustfs_service.upload_file。这体现了动静分离的架构思想，使得你的论坛应用具备了横向扩展（Scale-out）的能力。


果在答辩时老师问起这部分设计，你可以用以下专业术语来回答：
高并发设计：延迟同步机制 (Write-Behind / Async Sync)
话术：“为了应对论坛可能出现的高频收藏操作（如热帖被疯狂收藏），我没有让每次收藏都直接去写数据库（会造成数据库 IO 瓶颈）。而是先写 Redis，并利用 Redis Set (SYNC_PREFIX:users) 记录变动的用户 ID。后台会有定时任务（或异步 Worker）批量将数据同步到 MySQL，极大提升了接口的 QPS 吞吐量。”
Redis 高级数据结构的组合应用
ZSET (有序集合)：在 _get_user_bookmarks_key 中，你巧妙地利用 ZSET，以时间戳作为 Score，这让你可以轻松实现按收藏时间倒序分页（zrevrange），比数据库的 ORDER BY 快得多。
Hash (哈希表)：用 Hash 结构缓存帖子的详情 (HSET)，避免了频繁把整个 JSON 序列化和反序列化，支持对单个字段的修改。
网络 I/O 优化：Redis Pipeline (管道技术)
话术：“在添加/取消收藏时，涉及多个 Redis 命令（如 ZADD, INCR, HSET, EXPIRE）。我使用了 redis.pipeline() 将多条指令打包，一次性发送给 Redis 服务器执行，省去了多次网络往返时间 (RTT - Round Trip Time)，显著降低了响应延迟。”
缓存穿透/缺失处理 (Cache-Aside Pattern)
代码中的 get_user_bookmarks 实现了优雅的缓存回源逻辑：先查缓存 -> 找出 missing_ids -> 从 DB 批量查询 -> 写回 Redis -> 返回给前端。