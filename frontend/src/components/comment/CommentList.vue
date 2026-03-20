<template>
  <div class="comment-list">
    <!-- 加载中 -->
    <div v-if="loading && comments.length === 0" class="comment-loading">
      <CommentSkeleton :count="3" />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!loading && comments.length === 0" class="comment-empty">
      <el-empty description="暂无评论，快来抢沙发吧~" />
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="comment-error">
      <el-alert type="error" :closable="false">
        {{ error }}
        <el-button text type="info" @click="$emit('retry')">重试</el-button>
      </el-alert>
    </div>

    <!-- 评论列表 -->
    <template v-else>
      <div v-for="comment in comments" :key="comment.id" class="comment-list-item">
        <CommentItem
          :comment="comment"
          :post-id="postId"
          :active-reply-id="activeReplyId"
          :active-edit-id="activeEditId"
          :is-replying="activeReplyId === comment.id"
          :is-editing="activeEditId === comment.id"
          @reply="handleReply"
          @edit="handleEdit"
          @delete="handleDelete"
          @load-more="handleLoadMore"
          @cancel-reply="$emit('cancel-reply')"
          @cancel-edit="$emit('cancel-edit')"
          @comment-created="$emit('comment-created', $event)"
          @comment-updated="$emit('comment-updated', $event)"
        />
      </div>

      <!-- 加载更多 -->
      <div v-if="hasMore" class="load-more-root">
        <el-button
          :loading="loading"
          @click="$emit('load-more')"
        >
          加载更多评论
        </el-button>
      </div>

      <!-- 加载更多时的加载状态 -->
      <div v-if="loading && comments.length > 0" class="loading-more">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </template>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'
import CommentItem from './CommentItem.vue'
import CommentSkeleton from './CommentSkeleton.vue'

defineProps({
  comments: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  hasMore: {
    type: Boolean,
    default: false
  },
  postId: {
    type: Number,
    required: true
  },
  activeReplyId: {
    type: Number,
    default: null
  },
  activeEditId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits([
  'load-more',
  'retry',
  'reply',
  'edit',
  'delete',
  'load-more',
  'cancel-reply',
  'cancel-edit',
  'comment-created',
  'comment-updated'
])

const handleReply = (commentId) => emit('reply', commentId)
const handleEdit = (commentId) => emit('edit', commentId)
const handleDelete = (commentId) => emit('delete', commentId)
const handleLoadMore = (commentId) => emit('load-more', commentId)
</script>

<style scoped>
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-list-item {
  /* 分割线已移至 CommentItem 组件中 */
}

.comment-loading,
.comment-empty,
.comment-error {
  padding: 24px;
  text-align: center;
}

.load-more-root {
  padding: 16px;
  text-align: center;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #878a8c;
}

.loading-more .el-icon {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
