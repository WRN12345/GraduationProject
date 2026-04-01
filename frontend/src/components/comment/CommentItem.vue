<template>
  <div
    :class="['comment-item', `level-${level}`, { 'has-children': hasChildren }]"
    :id="`comment-${comment.id}`"
  >
    <!-- 辅助连线（可点击折叠）- 用户点击线条来展开/收起 -->
    <div
      v-if="level > 0"
      class="thread-line"
      :class="{ 
        'is-clickable': hasChildren, 
        'is-collapsed': isCollapsed,
        'is-loading': repliesLoading 
      }"
      @click="hasChildren ? toggleCollapse() : null"
    ></div>

    <!-- 评论主体 -->
    <div class="comment-body">
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
        :is-expanded="!isCollapsed"
        :replies-loading="repliesLoading"
        @reply="$emit('reply', comment.id)"
        @cancel-reply="$emit('cancel-reply')"
        @edit="$emit('edit', comment.id)"
        @delete="$emit('delete', comment.id)"
        @load-more="$emit('load-more', comment.id)"
        @toggle-collapse="toggleCollapse"
      />

      <!-- 回复编辑器 -->
      <CommentReplyEditor
        v-if="activeReplyId === comment.id"
        :post-id="postId"
        :parent-comment="comment"
        @submit="handleReplySubmit"
        @cancel="$emit('cancel-reply')"
      />

      <!-- 折叠状态提示 - 点击线条或此按钮可展开 -->
      <div v-if="isCollapsed && hiddenReplyCount > 0" class="collapsed-hint" @click="toggleCollapse">
        <span class="collapse-icon">▶</span>
        <span>{{ t('comment.expandReplies', { count: hiddenReplyCount }) }}</span>
      </div>
    </div>

    <!-- 子评论列表容器（带动画） -->
    <Transition
      name="replies-collapse"
      @before-enter="beforeEnter"
      @enter="enter"
      @leave="leave"
    >
      <div 
        v-if="!isCollapsed && comment.replies?.length > 0" 
        ref="repliesContainer"
        class="comment-replies"
      >
        <TransitionGroup name="reply-item" appear>
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
        </TransitionGroup>
      </div>
    </Transition>

    <!-- 加载更多子评论 -->
    <Transition name="fade">
      <div
        v-if="comment.has_more_replies && !isCollapsed && !repliesLoading"
        class="load-more-replies"
      >
        <el-button text @click="$emit('load-more', comment.id)">
          {{ t('comment.loadMoreReplies', { count: comment.reply_count - (comment.replies?.length || 0) }) }}
        </el-button>
      </div>
    </Transition>

    <!-- 子评论加载中 -->
    <Transition name="fade">
      <div v-if="repliesLoading" class="replies-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>{{ t('comment.loading') }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { client } from '@/api/client'
import CommentContent from './CommentContent.vue'
import CommentActions from './CommentActions.vue'
import CommentReplyEditor from './CommentReplyEditor.vue'

const { t } = useI18n()

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
const repliesContainer = ref(null)

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
  if (repliesLoading.value) return
  isCollapsed.value = !isCollapsed.value
}

// Transition hooks for smooth height animation
const beforeEnter = (el) => {
  el.style.height = '0'
  el.style.opacity = '0'
  el.style.overflow = 'hidden'
}

const enter = (el) => {
  const height = el.scrollHeight
  el.style.height = height + 'px'
  el.style.opacity = '1'
  
  // After animation, remove fixed height for responsive content
  setTimeout(() => {
    el.style.height = 'auto'
  }, 300)
}

const leave = (el) => {
  const height = el.scrollHeight
  el.style.height = height + 'px'
  // Force reflow
  el.offsetHeight
  el.style.height = '0'
  el.style.opacity = '0'
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
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.comment-item:last-child {
  border-bottom: none;
}

/* 根评论无缩进 */
.comment-item.level-0 {
  padding-left: 0;
}

/* 子评论左侧留出辅助连线空间 - 增加缩进量 */
.comment-item:not(.level-0) {
  padding-left: 32px;
  margin-left: 16px;
}

/* 评论主体 */
.comment-body {
  position: relative;
  z-index: 2;
}

/* 辅助连线 - 从父评论头像中线开始垂直向下，可点击展开/收起 */
.thread-line {
  position: absolute;
  left: 11px;
  top: 28px;
  bottom: 0;
  width: 1px;
  background: #eee;
  transition: all 0.2s ease;
  z-index: 1;
}

/* 可点击状态 */
.thread-line.is-clickable {
  cursor: pointer;
}

/* Hover效果：颜色加深(#999)，宽度变粗(2px) */
.thread-line.is-clickable:hover {
  background: #999;
  width: 2px;
  left: 10px;
}

/* 折叠状态 - 线条颜色略深以便提示 */
.thread-line.is-collapsed {
  background: #e0e0e0;
}

/* 加载状态 */
.thread-line.is-loading {
  background: #ccc;
}

/* 折叠状态提示 - 轻量级文本按钮 */
.collapsed-hint {
  padding: 8px 0 8px 24px;
  margin-top: 8px;
  cursor: pointer;
  color: #999;
  font-size: 13px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  user-select: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.collapsed-hint:hover {
  color: #0079d3;
}

.collapse-icon {
  transition: transform 0.2s ease;
  font-size: 10px;
}

/* 子评论列表容器 */
.comment-replies {
  margin-top: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 加载更多 */
.load-more-replies {
  margin-top: 8px;
  padding-left: 24px;
}

.replies-loading {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: #0079d3;
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

/* 抽屉式折叠动画 */
.replies-collapse-enter-active,
.replies-collapse-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.replies-collapse-enter-from,
.replies-collapse-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 子评论项依次出现动画 */
.reply-item-enter-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  transition-delay: 0.05s;
}

.reply-item-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.reply-item-enter-from {
  opacity: 0;
  transform: translateY(-15px);
}

.reply-item-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 移动端适配 */
@media (max-width: 639px) {
  .comment-item:not(.level-0) {
    padding-left: 24px;
    margin-left: 12px;
  }

  .thread-line {
    left: 8px;
  }

  .thread-line.is-clickable:hover {
    left: 7px;
  }

  .load-more-replies {
    padding-left: 16px;
  }

  .collapsed-hint {
    padding-left: 18px;
  }
}
</style>
