<script setup>
import { ref } from 'vue'
import {
  ThumbsUp,
  ThumbsDown,
  MessageCircle,
  Bookmark,
  Share2,
  Send
} from 'lucide-vue-next'

// 模拟帖子数据
const posts = ref([
  {
    id: 1,
    subreddit: 'r/RedditGames',
    user: 'u/OK_Schedule4494',
    time: '15小时前',
    title: 'Shit level 垃圾水平',
    type: 'image',
    content: '/assets/image/1.jpg',
    votes: 300,
    comments: 274
  },
  {
    id: 2,
    subreddit: 'r/QuizPlanetGame',
    user: 'u/czs250',
    time: '1天前',
    title: 'Cybersecurity quiz 网络安全测验',
    type: 'quiz',
    content: 'What is the most vulnerable OSI model layer?',
    votes: 120,
    comments: 45
  }
])

// 评论输入
const commentInputs = ref({})
</script>

<template>
  <!-- Feed 流 -->
  <div class="feed-container">
    <!-- 帖子循环 -->
    <div class="post-card" v-for="post in posts" :key="post.id">
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
          <div class="image-placeholder">
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

        <!-- 底部操作区 -->
        <div class="post-footer">
          <!-- 左侧：点赞点踩 -->
          <div class="footer-left">
            <button class="vote-action-btn">
              <ThumbsUp :size="18" />
              <span>{{ post.votes }}</span>
            </button>
            <button class="vote-action-btn">
              <ThumbsDown :size="18" />
            </button>
          </div>

          <!-- 右侧：评论收藏转发 -->
          <div class="footer-right">
            <button class="action-btn" title="评论">
              <MessageCircle :size="18" />
              <span>{{ post.comments }}</span>
            </button>
            <button class="action-btn" title="收藏">
              <Bookmark :size="18" />
            </button>
            <button class="action-btn" title="转发">
              <Share2 :size="18" />
            </button>
          </div>
        </div>

        <!-- 评论输入框 -->
        <div class="comment-input-wrapper">
          <div class="comment-input">
            <input
              type="text"
              v-model="commentInputs[post.id]"
              placeholder="善语结善缘，恶语伤人心"
              class="comment-field"
            />
            <button class="send-btn" title="发送">
              <Send :size="16" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Feed 样式 */
.feed-container {
  width: 100%;
  max-width: 980px;
  margin: 0 auto;
}

.post-card {
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: border-color 0.2s;
}

.post-card:hover {
  border-color: #0079d3;
}

.post-content {
  padding: 12px 16px;
}

.post-header {
  font-size: 12px;
  color: #787c7e;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.subreddit-name {
  font-weight: 600;
  color: #1c1c1c;
}

.subreddit-name:hover {
  text-decoration: underline;
}

.post-title {
  font-size: 18px;
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #1c1c1c;
  line-height: 1.4;
}

.mock-image {
  background: #000;
  color: #fff;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: monospace;
  border-radius: 8px;
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
  background: #fff;
  color: #1a1a1b;
  font-weight: 600;
  transition: background 0.2s;
}

.quiz-options button:hover {
  background: #f0f0f0;
}

/* 底部操作区 */
.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #edeff1;
}

.footer-left {
  display: flex;
  gap: 4px;
}

.footer-right {
  display: flex;
  gap: 4px;
}

.vote-action-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  color: #878a8c;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.vote-action-btn:hover {
  background: #f6f7f8;
  color: #1c1c1c;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px 12px;
  color: #878a8c;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f6f7f8;
  color: #1c1c1c;
}

/* 评论输入框 */
.comment-input-wrapper {
  margin-top: 12px;
}

.comment-input {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f6f7f8;
  border: 1px solid transparent;
  border-radius: 24px;
  padding: 8px 16px;
  transition: all 0.2s;
}

.comment-input:focus-within {
  background: #fff;
  border-color: #0079d3;
  box-shadow: 0 0 0 2px rgba(0, 121, 211, 0.1);
}

.comment-field {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #1c1c1c;
}

.comment-field::placeholder {
  color: #878a8c;
  font-style: italic;
}

.send-btn {
  background: none;
  border: none;
  color: #0079d3;
  cursor: pointer;
  padding: 6px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.send-btn:hover {
  background: rgba(0, 121, 211, 0.1);
}

.send-btn:disabled {
  color: #ccc;
  cursor: not-allowed;
}

/* === 响应式优化 === */

/* 小窗口 (< 640px) */
@media (max-width: 639px) {
  .feed-container {
    max-width: 100%;
    padding: 0;
  }

  .post-card {
    border-radius: 0;
    border-left: none;
    border-right: none;
    margin-bottom: 0;
  }

  .post-card:first-child {
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

  .post-content {
    padding: 12px;
  }

  .post-title {
    font-size: 16px;
  }

  .post-footer {
    flex-wrap: wrap;
    gap: 4px;
  }

  .footer-left,
  .footer-right {
    gap: 2px;
  }

  .vote-action-btn,
  .action-btn {
    padding: 6px 8px;
    font-size: 12px;
  }

  .comment-input {
    padding: 6px 12px;
  }
}

/* 中小窗口 (640px - 767px) */
@media (min-width: 640px) and (max-width: 767px) {
  .feed-container {
    max-width: 100%;
  }

  .post-content {
    padding: 14px 16px;
  }

  .post-title {
    font-size: 17px;
  }
}

/* 中等窗口 (768px - 959px) */
@media (min-width: 768px) and (max-width: 959px) {
  .feed-container {
    max-width: 100%;
  }

  .post-content {
    padding: 14px 16px;
  }
}

/* 大窗口 (960px - 1279px) */
@media (min-width: 960px) and (max-width: 1279px) {
  .feed-container {
    max-width: 980px;
  }
}

/* 超大窗口 (>= 1280px) */
@media (min-width: 1280px) {
  .feed-container {
    max-width: 980px;
  }
}
</style>