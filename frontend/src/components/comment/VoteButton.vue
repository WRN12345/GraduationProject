<template>
  <div class="vote-button">
    <button
      :class="['vote-btn', 'like', { active: userVote === 1 }]"
      @click="handleVote(1)"
      :disabled="loading"
      title="喜欢"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M8 13.5L2.5 8C1 6.5 1 4 2.5 2.5C4 1 6.5 1 8 2.5C9.5 1 12 1 13.5 2.5C15 4 15 6.5 13.5 8L8 13.5Z"/>
      </svg>
      <span class="vote-count" v-if="upvotes > 0">{{ upvotes }}</span>
    </button>

    <button
      :class="['vote-btn', 'dislike', { active: userVote === -1 }]"
      @click="handleVote(-1)"
      :disabled="loading"
      title="不喜欢"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <path d="M13.5 8L8 13.5L2.5 8C1 6.5 1 4 2.5 2.5C4 1 6.5 1 8 2.5C9.5 1 12 1 13.5 2.5C15 4 15 6.5 13.5 8ZM5.5 5.5L8 8L10.5 5.5"/>
      </svg>
      <span class="vote-count" v-if="downvotes > 0">{{ downvotes }}</span>
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
        if (direction === 1) {
          downvotes.value--
          upvotes.value++
        } else {
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
  gap: 4px;
}

.vote-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #878a8c;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.vote-btn:hover:not(:disabled) {
  background: #f6f7f8;
  color: #1c1c1c;
}

.vote-btn.like.active {
  color: #ff1744;
}

.vote-btn.dislike.active {
  color: #757575;
}

.vote-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.vote-count {
  font-weight: 600;
  font-size: 12px;
}
</style>
