<template>
  <div
    :class="['comment-item', `level-${level}`, { 'has-children': hasChildren }]"
    :id="`comment-${comment.id}`"
  >
    <!-- 辅助连线（可点击折叠） -->
    <div
      v-if="level > 0"
      class="thread-line"
      :class="{ 'is-clickable': hasChildren, 'collapsed': isCollapsed }"
      @click="hasChildren ? toggleCollapse() : null"
    >
      <!-- 折叠/展开按钮 -->
      <span v-if="hasChildren" class="thread-collapse-btn" @click.stop="toggleCollapse()">
        <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
          <path d="M2 3L5 7L8 3H2Z"/>
        </svg>
      </span>
    </div>

    <!-- 评论内容 -->
    <CommentContent
      :comment="comment"
      :is-deleted="!!comment.deleted_at"
      :is-editing="activeEditId === comment.id"
      @edit-save="handleEditSave"
      @vote-changed="handleVoteChanged"
    />

    <!-- 操作栏 -->
    <CommentActions
      :comment="comment"
      :is-replying="activeReplyId === comment.id"
      :can-edit="canEdit"
      :can-delete="canDelete"
      @reply="$emit('reply', comment.id)"
      @edit="$emit('edit', comment.id)"
      @delete="$emit('delete', comment.id)"
      @load-more="$emit('load-more', comment.id)"
    />

    <!-- 回复编辑器 -->
    <CommentReplyEditor
      v-if="activeReplyId === comment.id"
      :post-id="postId"
      :parent-comment="comment"
      @submit="handleReplySubmit"
      @cancel="$emit('cancel-reply')"
    />

    <!-- 折叠状态提示 -->
    <div v-if="isCollapsed && hiddenReplyCount > 0" class="collapsed-hint" @click="toggleCollapse">
      <span class="collapse-icon">▶</span>
      <span>{{ hiddenReplyCount }} 条隐藏回复</span>
    </div>

    <!-- 子评论列表（递归） - 只在未折叠时显示 -->
    <div v-if="!isCollapsed && comment.replies?.length > 0" class="comment-replies">
      <CommentItem
        v-for="reply in comment.replies"
        :key="reply.id"
        :comment="reply"
        :post-id="postId"
        :level="Math.min(level + 1, maxLevel)"
        :max-level="maxLevel"
        :active-reply-id="activeReplyId"
        :active-edit-id="activeEditId"
        :is-replying="activeReplyId === reply.id"
        :is-editing="activeEditId === reply.id"
        @reply="handleNestedReply"
        @edit="handleNestedEdit"
        @delete="handleNestedDelete"
        @load-more="handleNestedLoadMore"
        @cancel-reply="$emit('cancel-reply')"
        @cancel-edit="$emit('cancel-edit')"
        @comment-created="$emit('comment-created', $event)"
        @comment-updated="$emit('comment-updated', $event)"
      />
    </div>

    <!-- 加载更多子评论 -->
    <div
      v-if="comment.has_more_replies && !isCollapsed && !repliesLoading"
      class="load-more-replies"
    >
      <el-button text @click="$emit('load-more', comment.id)">
        加载更多回复 ({{ comment.reply_count - (comment.replies?.length || 0) }})
      </el-button>
    </div>

    <!-- 子评论加载中 -->
    <div v-if="repliesLoading" class="replies-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { client } from '@/api/client'
import CommentContent from './CommentContent.vue'
import CommentActions from './CommentActions.vue'
import CommentReplyEditor from './CommentReplyEditor.vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  postId: {
    type: Number,
    required: true
  },
  level: {
    type: Number,
    default: 0
  },
  maxLevel: {
    type: Number,
    default: 5
  },
  isReplying: {
    type: Boolean,
    default: false
  },
  isEditing: {
    type: Boolean,
    default: false
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
  'reply',
  'edit',
  'delete',
  'load-more',
  'cancel-reply',
  'cancel-edit',
  'comment-created',
  'comment-updated',
  'vote-changed'
])

const userStore = useUserStore()
const repliesLoading = computed(() => props.comment._loading)

// 折叠状态管理
const isCollapsed = ref(false)

// 计算是否有子评论
const hasChildren = computed(() =>
  props.comment.replies && props.comment.replies.length > 0
)

// 计算隐藏的子评论数量
const hiddenReplyCount = computed(() => {
  if (!isCollapsed.value) return 0
  const countReplies = (comment) => {
    let count = comment.replies?.length || 0
    for (const reply of comment.replies || []) {
      count += countReplies(reply)
    }
    return count
  }
  return countReplies(props.comment)
})

// 切换折叠状态
const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

const canEdit = computed(() =>
  userStore.userId === props.comment.author_id
)

const canDelete = computed(() =>
  userStore.userId === props.comment.author_id || userStore.isSuperuser
)

// 处理回复提交
const handleReplySubmit = async (content) => {
  try {
    const response = await client.POST('/v1/comments', {
      body: {
        content,
        post_id: props.postId,
        parent_id: props.comment.id
      }
    })

    if (response.data) {
      // 添加到子评论列表
      if (!props.comment.replies) {
        props.comment.replies = []
      }
      props.comment.replies.push(response.data)
      props.comment.reply_count++

      emit('comment-created', response.data)
      emit('cancel-reply')
      ElMessage.success('回复成功')
    }
  } catch (error) {
    console.error('回复失败:', error)
    ElMessage.error('回复失败')
  }
}

// 处理编辑保存
const handleEditSave = async (newContent) => {
  try {
    const response = await client.PUT('/v1/comments/{comment_id}', {
      params: { path: { comment_id: props.comment.id } },
      body: { content: newContent }
    })

    if (response.data) {
      props.comment.content = response.data.content
      props.comment.is_edited = response.data.is_edited
      props.comment.updated_at = response.data.updated_at

      emit('comment-updated', response.data)
      emit('cancel-edit')
      ElMessage.success('编辑成功')
    }
  } catch (error) {
    console.error('编辑失败:', error)
    ElMessage.error('编辑失败')
  }
}

// 递归事件处理
const handleNestedReply = (commentId) => emit('reply', commentId)
const handleNestedEdit = (commentId) => emit('edit', commentId)
const handleNestedDelete = (commentId) => emit('delete', commentId)
const handleNestedLoadMore = (commentId) => emit('load-more', commentId)

// 处理投票变化
const handleVoteChanged = (voteData) => {
  props.comment.user_vote = voteData.userVote
  props.comment.score = voteData.score
  emit('vote-changed', voteData)
}
</script>

<style scoped>
.comment-item {
  position: relative;
  padding: 12px 0;
}

/* 根评论无缩进 */
.comment-item.level-0 {
  padding-left: 0;
}

/* 子评论左侧留出辅助连线空间 */
.comment-item:not(.level-0) {
  padding-left: 40px;
  margin-left: 8px;
}

/* 辅助连线 - 可点击折叠 */
.thread-line {
  position: absolute;
  left: 12px;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #edeff1;
  transition: all 0.2s;
  border-radius: 2px;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thread-line.is-clickable {
  cursor: pointer;
}

.thread-line.is-clickable:hover {
  background: #c8cdd0;
  width: 6px;
  left: 11px;
}

.thread-line.collapsed {
  background: #0079d3;
}

/* 折叠/展开按钮 */
.thread-collapse-btn {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: 18px;
  height: 18px;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #878a8c;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 2;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.thread-line.is-clickable:hover .thread-collapse-btn {
  border-color: #0079d3;
  color: #0079d3;
  box-shadow: 0 2px 6px rgba(0, 121, 211, 0.2);
}

.thread-line.collapsed .thread-collapse-btn {
  border-color: #0079d3;
  color: #0079d3;
  background: #f0f6fc;
}

.thread-collapse-btn svg {
  transition: transform 0.2s ease;
}

/* 折叠时图标向右旋转 */
.thread-line.collapsed .thread-collapse-btn svg {
  transform: rotate(-90deg);
}

/* 折叠状态提示 */
.collapsed-hint {
  padding: 8px 0 8px 24px;
  margin-top: 8px;
  cursor: pointer;
  color: #878a8c;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  user-select: none;
  border-radius: 4px;
  transition: all 0.2s;
}

.collapsed-hint:hover {
  color: #0079d3;
  background: #f6f7f8;
}

.collapse-icon {
  transition: transform 0.2s;
  font-size: 10px;
}

.comment-replies {
  margin-top: 12px;
}

.load-more-replies {
  margin-top: 8px;
  padding-left: 24px;
}

.replies-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: #878a8c;
  font-size: 14px;
}

.replies-loading .el-icon {
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

/* 移动端适配 */
@media (max-width: 639px) {
  .comment-item:not(.level-0) {
    padding-left: 28px;
  }

  .thread-line {
    left: 8px;
  }

  .thread-line.is-clickable:hover {
    left: 7px;
  }

  .thread-collapse-btn {
    width: 16px;
    height: 16px;
    top: 14px;
  }

  .load-more-replies {
    padding-left: 16px;
  }

  .collapsed-hint {
    padding-left: 18px;
  }
}
</style>
