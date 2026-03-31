<template>
  <div class="comment-tree">
    <!-- 头部统计和操作 -->
    <div class="comment-header">
      <h3 class="comment-title">{{ t('comment.title', { count: totalComments }) }}</h3>
      <el-button
        text
        :icon="RefreshCw"
        @click="refreshComments"
        :loading="commentsLoading"
      >
        {{ t('comment.refresh') }}
      </el-button>
    </div>

    <!-- 主编辑器 -->
    <CommentEditor
      v-if="userStore.isLoggedIn"
      :post-id="postId"
      :placeholder="t('comment.placeholder')"
      @submit="handleCreateComment"
    />
    <div v-else class="login-tip">
      {{ t('comment.loginTip') }} <router-link to="/login">{{ t('comment.login') }}</router-link> {{ t('comment.loginSuffix') }}
    </div>

    <!-- 输入区与评论列表之间的分割线 -->
    <div class="section-divider"></div>

    <!-- 评论列表 -->
    <CommentList
      :comments="comments"
      :loading="commentsLoading"
      :error="commentsError"
      :has-more="hasMoreRootComments"
      :post-id="postId"
      :active-reply-id="activeReplyId"
      :active-edit-id="activeEditId"
      @load-more="handleLoadMoreReplies"
      @reply="handleReply"
      @edit="handleEdit"
      @delete="handleDelete"
      @cancel-reply="activeReplyId = null"
      @cancel-edit="activeEditId = null"
      @comment-created="handleChildCommentCreated"
      @comment-updated="handleCommentUpdated"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useUserStore } from '@/stores/user'
import { RefreshCw } from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { client } from '@/api/client'
import CommentEditor from './CommentEditor.vue'
import CommentList from './CommentList.vue'

const { t } = useI18n()

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  initialRootLimit: {
    type: Number,
    default: 20
  },
  replyLimit: {
    type: Number,
    default: 3
  }
})

const emit = defineEmits(['comment-count-change', 'comment-created'])

const userStore = useUserStore()

// 状态
const comments = ref([])
const commentsLoading = ref(false)
const commentsError = ref(null)
const totalComments = ref(0)
const hasMoreRootComments = ref(false)

// 分页状态
const rootOffset = ref(0)
const rootLimit = ref(props.initialRootLimit)

// 交互状态
const activeReplyId = ref(null)
const activeEditId = ref(null)

// 加载根评论
const loadRootComments = async (refresh = false) => {
  if (refresh) {
    rootOffset.value = 0
    comments.value = []
  }

  commentsLoading.value = true
  commentsError.value = null

  try {
    const response = await client.GET('/v1/posts/{post_id}/comments', {
      params: {
        path: { post_id: props.postId },
        query: {
          root_offset: rootOffset.value,
          root_limit: rootLimit.value,
          reply_limit: props.replyLimit
        }
      }
    })

    if (response.data) {
      const newComments = response.data

      if (refresh) {
        comments.value = newComments
      } else {
        comments.value.push(...newComments)
      }

      // 更新总数和分页状态
      totalComments.value = newComments.length || 0
      hasMoreRootComments.value = newComments.length >= rootLimit.value
      rootOffset.value += newComments.length

      emit('comment-count-change', totalComments.value)
    }
  } catch (error) {
    console.error('加载评论失败:', error)
    commentsError.value = t('comment.loadFailed')
    ElMessage.error(t('comment.loadCommentsFailed'))
  } finally {
    commentsLoading.value = false
  }
}

// 加载更多根评论
const loadMoreRootComments = () => {
  loadRootComments(false)
}

// 刷新评论
const refreshComments = () => {
  loadRootComments(true)
}

// 创建评论
const handleCreateComment = async (content) => {
  try {
    const response = await client.POST('/v1/comments', {
      body: {
        content,
        post_id: props.postId,
        parent_id: null
      }
    })

    if (response.data) {
      // 添加到列表顶部
      comments.value.unshift(response.data)
      totalComments.value++
      emit('comment-created', response.data)
      ElMessage.success(t('comment.postSuccess'))
    }
  } catch (error) {
    console.error('发表评论失败:', error)
    ElMessage.error(t('comment.postFailed'))
  }
}

// 回复评论
const handleReply = (commentId) => {
  activeReplyId.value = commentId
  activeEditId.value = null
}

// 编辑评论
const handleEdit = (commentId) => {
  activeEditId.value = commentId
  activeReplyId.value = null
}

// 删除评论
const handleDelete = async (commentId) => {
  try {
    await client.DELETE('/v1/comments/{comment_id}', {
      params: { path: { comment_id: commentId } }
    })

    // 从列表中移除
    const removeComment = (list) => {
      for (let i = 0; i < list.length; i++) {
        if (list[i].id === commentId) {
          list.splice(i, 1)
          return true
        }
        if (list[i].replies?.length > 0) {
          if (removeComment(list[i].replies)) return true
        }
      }
      return false
    }

    removeComment(comments.value)
    totalComments.value--
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('删除评论失败:', error)
    ElMessage.error('删除失败')
  }
}

// 子评论创建成功
const handleChildCommentCreated = (comment) => {
  totalComments.value++
  emit('comment-created', comment)
}

// 评论更新成功
const handleCommentUpdated = (comment) => {
  ElMessage.success('编辑成功')
}

// 处理加载更多回复 / 加载更多根评论
const handleLoadMoreReplies = async (commentId) => {
  // 如果没有 commentId，加载更多根评论
  if (!commentId) {
    loadMoreRootComments()
    return
  }

  // 递归查找并更新评论
  const findAndUpdateComment = (commentList) => {
    for (const comment of commentList) {
      if (comment.id === commentId) {
        // 找到目标评论，加载更多回复
        loadMoreReplies(comment)
        return true
      }
      if (comment.replies?.length > 0) {
        if (findAndUpdateComment(comment.replies)) return true
      }
    }
    return false
  }

  findAndUpdateComment(comments.value)
}

// 加载更多回复的具体实现
const loadMoreReplies = async (comment) => {
  // 设置加载状态
  comment._loading = true

  try {
    // 计算当前偏移量
    const currentLength = comment.replies?.length || 0

    const response = await client.GET('/v1/posts/{post_id}/comments/{parent_id}/replies', {
      params: {
        path: { post_id: props.postId, parent_id: comment.id },
        query: { offset: currentLength, limit: 20 }
      }
    })

    if (response.data) {
      // 添加新回复
      if (!comment.replies) {
        comment.replies = []
      }
      comment.replies.push(...response.data.replies)

      // 更新状态
      comment.has_more_replies = response.data.has_more
    }
  } catch (error) {
    console.error('加载更多回复失败:', error)
    ElMessage.error('加载失败')
  } finally {
    comment._loading = false
  }
}

onMounted(() => {
  loadRootComments()
})
</script>

<style scoped>
.comment-tree {
  padding: 24px 0;
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.comment-title {
  font-size: 15px;
  font-weight: 500;
  color: #666;
  margin: 0;
}

.login-tip {
  padding: 16px;
  background: #f6f7f8;
  border-radius: 8px;
  text-align: center;
  color: #878a8c;
  margin-bottom: 16px;
}

.login-tip a {
  color: #0079d3;
  text-decoration: none;
  font-weight: 600;
}

.login-tip a:hover {
  text-decoration: underline;
}

.section-divider {
  border-bottom: 1px solid #f0f0f0;
  margin: 20px 0;
}
</style>
