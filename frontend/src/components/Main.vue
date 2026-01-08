<script setup>
import { ref } from 'vue'

// 模拟帖子数据
const posts = ref([
  {
    id: 1,
    subreddit: 'r/RedditGames',
    user: 'u/OK_Schedule4494',
    time: '15小时前',
    title: 'Shit level 垃圾水平',
    type: 'image',
    content: '/assets/image/1.jpg', // 这里需要对应你本地的图片路径
    votes: 300,
    comments: 274
  },
  {
    id: 2,
    subreddit: 'r/QuizPlanetGame',
    user: 'u/czs250',
    time: '1天前',
    title: 'Cybersecurity quiz 网络安全测验',
    type: 'quiz', // 模拟不同类型的帖子样式
    content: 'What is the most vulnerable OSI model layer?',
    votes: 120,
    comments: 45
  }
])
</script>

<template>
  <!-- 中间 Feed 流 -->
  <div class="feed-container">
    <!-- 帖子循环 -->
    <div class="post-card" v-for="post in posts" :key="post.id">
      <!-- 投票侧边 -->
      <div class="vote-section">
        <button class="vote-btn">⬆</button>
        <span class="vote-count">{{ post.votes }}</span>
        <button class="vote-btn">⬇</button>
      </div>

      <!-- 帖子内容 -->
      <div class="post-content">
        <div class="post-header">
          <span class="subreddit-icon">👾</span>
          <span class="subreddit-name">{{ post.subreddit }}</span>
          <span class="meta-info">· 由 {{ post.user }} 发布 · {{ post.time }}</span>
        </div>
        
        <h3 class="post-title">{{ post.title }}</h3>

        <!-- 根据类型显示图片或文本 -->
        <div class="post-media" v-if="post.type === 'image'">
          <!-- 这里使用 img 标签，实际项目可能需要动态引入 -->
          <div class="image-placeholder">
             <!-- 这里的 img src 需要处理，为了演示用背景色代替 -->
             <div class="mock-image">GAME SCREENSHOT ({{post.id}})</div>
          </div>
        </div>

        <div class="post-media quiz-style" v-else>
           <div class="quiz-content">
              <h4>{{ post.content }}</h4>
              <div class="quiz-options">
                <button>L1 Physical Layer</button>
                <button>L7 Application Layer</button>
              </div>
           </div>
        </div>

        <div class="post-footer">
          <button class="action-btn">💬 {{ post.comments }} 条评论</button>
          <button class="action-btn">↪ 共享</button>
          <button class="action-btn">🔖 收藏</button>
        </div>
      </div>
    </div>
  </div>

  <!-- 右侧边栏 -->
  <div class="right-sidebar">
    <div class="sidebar-card">
      <div class="card-header">
        <h4>近期帖子</h4>
        <span class="clear-btn">清除</span>
      </div>
      <ul class="recent-list">
        <li>
          <div class="recent-item">
            <span class="item-icon">R</span>
            <div class="item-text">
              <div class="item-title">Yep 50 是的 50</div>
              <div class="item-meta">37 个点赞 · 51 条评论</div>
            </div>
          </div>
        </li>
        <li>
          <div class="recent-item">
            <span class="item-icon">N</span>
            <div class="item-text">
              <div class="item-title">法官下令释放...</div>
              <div class="item-meta">4万 个点赞 · 967 条评论</div>
            </div>
            <div class="item-img-small"></div>
          </div>
        </li>
      </ul>
    </div>

    <div class="sidebar-card policy-card">
      <div class="policy-links">
        Reddit 规则 · 隐私政策 · 用户协议
      </div>
      <div class="copyright">Reddit, Inc. © 2025。保留所有权利。</div>
    </div>
  </div>
</template>

<style scoped>
/* Feed 样式 */
.feed-container {
  flex: 1; /* 占据剩余空间 */
  min-width: 0; /* 防止flex子项溢出 */
}

.post-card {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
  display: flex;
  cursor: pointer;
}
.post-card:hover {
  border-color: #898989;
}

.vote-section {
  width: 40px;
  background: #f8f9fa;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
  border-right: 1px solid transparent; /* 视觉对齐 */
}
.vote-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #878a8c;
}
.vote-btn:hover { color: #cc3700; background: #e9e9e9; border-radius: 4px; }
.vote-count {
  font-weight: bold;
  font-size: 12px;
  margin: 4px 0;
}

.post-content {
  padding: 8px;
  flex: 1;
}

.post-header {
  font-size: 12px;
  color: #787c7e;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.subreddit-name {
  font-weight: bold;
  color: #1c1c1c;
}
.subreddit-name:hover { text-decoration: underline; }

.post-title {
  font-size: 18px;
  margin: 0 0 10px 0;
  font-weight: 500;
}

.mock-image {
  background: #000;
  color: #fff;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: monospace;
}
.quiz-style {
  background: #1a1a1b;
  color: white;
  padding: 20px;
  border-radius: 8px;
}
.quiz-options button {
  display: block;
  width: 100%;
  margin: 5px 0;
  padding: 10px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
}

.post-footer {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
.action-btn {
  background: none;
  border: none;
  padding: 6px 10px;
  color: #878a8c;
  font-size: 12px;
  font-weight: 700;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.action-btn:hover { background: #e8e8e8; }

/* 右侧栏样式 */
.right-sidebar {
  width: 310px;
  display: none;
}

@media (min-width: 960px) {
  .right-sidebar {
    display: block;
  }
}

.sidebar-card {
  background: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 15px;
  padding: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}
.card-header h4 { margin: 0; font-size: 14px; text-transform: uppercase; color: #787c7e; }
.clear-btn { font-size: 12px; color: #0079d3; cursor: pointer; }

.recent-list {
  list-style: none;
}
.recent-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.item-icon {
  width: 20px;
  height: 20px;
  background: #0079d3;
  border-radius: 50%;
  color: white;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.item-text { flex: 1; }
.item-title { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.item-meta { font-size: 12px; color: #787c7e; }
.item-img-small { width: 60px; height: 45px; background: #333; border-radius: 4px; }

.policy-links { font-size: 12px; color: #787c7e; margin-bottom: 5px; }
.copyright { font-size: 12px; color: #787c7e; }
</style>