<template>
  <div class="vote-button">
    <button
      :class="['vote-btn', 'like', { active: userVote === 1 }]"
      @click="handleVote(1)"
      :disabled="loading"
      title="赞"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/>
      </svg>
      <span class="vote-count">{{ upvotes }}</span>
    </button>

    <button
      :class="['vote-btn', 'dislike', { active: userVote === -1 }]"
      @click="handleVote(-1)"
      :disabled="loading"
      title="踩"
    >
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"/>
      </svg>
      <span class="vote-count">{{ downvotes }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { client } from '@/api/client'
import { ElMessage } from 'element-plus'

const props = defineProps({
  commentId: {
    type: Number,
    required: true
  },
  initialUpvotes: {
    type: Number,
    default: 0
  },
  initialDownvotes: {
    type: Number,
    default: 0
  },
  initialScore: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['vote-changed'])

const userVote = ref(0)
const upvotes = ref(props.initialUpvotes)
const downvotes = ref(props.initialDownvotes)
const score = ref(props.initialScore)
const loading = ref(false)

const loadVoteStatus = async () => {
  try {
    const response = await client.GET('/v1/comments/{comment_id}/vote', {
      params: { path: { comment_id: props.commentId } }
    })
    if (response.data) {
      userVote.value = response.data.user_vote || 0
      upvotes.value = response.data.upvotes || 0
      downvotes.value = response.data.downvotes || 0
      score.value = response.data.score
    }
  } catch (error) {
    // 未登录或忽略错误
  }
}

const handleVote = async (direction) => {
  loading.value = true
  try {
    const newDirection = userVote.value === direction ? 0 : direction
    const response = await client.POST('/v1/vote', {
      body: {
        comment_id: props.commentId,
        direction: newDirection
      }
    })

    if (response.data) {
      const delta = response.data.delta

      if (userVote.value === direction) {
        userVote.value = 0
        if (direction === 1) upvotes.value--
        else downvotes.value--
      } else if (userVote.value === 0) {
        userVote.value = direction
        if (direction === 1) upvotes.value++
        else downvotes.value++
      } else {
        // 改变投票方向：从赞变为踩，或从踩变为赞
        if (direction === 1) {
          // 从踩变为赞：点踩数-1，点赞数+1
          downvotes.value--
          upvotes.value++
        } else {
          // 从赞变为踩：点赞数-1，点踩数+1
          upvotes.value--
          downvotes.value++
        }
        userVote.value = direction
      }

      score.value += delta
      emit('vote-changed', { userVote: userVote.value, score: score.value })
    }
  } catch (error) {
    console.error('投票失败:', error)
    ElMessage.error('投票失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadVoteStatus()
})

defineExpose({
  loadVoteStatus
})
</script>

<style scoped>
.vote-button {
  display: flex;
  align-items: center;
  gap: 2px;
}

.vote-btn {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 4px 6px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #999999;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.vote-btn:hover:not(:disabled) {
  background: #f6f7f8;
  color: #1c1c1c;
}

.vote-btn.like.active {
  color: #0079d3;
}

.vote-btn.dislike.active {
  color: #ff4500;
}

.vote-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vote-count {
  font-weight: 500;
  font-size: 12px;
  min-width: 16px;
  text-align: center;
}
</style>
