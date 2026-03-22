<template>
  <div class="vote-buttons" @click.stop>
    <!-- 点赞按钮 -->
    <button
      :class="['vote-btn', 'upvote', { active: userVote === 1 }]"
      @click="() => handleVote(1)"
      :disabled="loading"
      :title="userVote === 1 ? '取消点赞' : '点赞'"
    >
      <ThumbsUp :size="iconSize" :class="{ 'icon-spin': loading && userVote === 1 }" />
      <span v-if="showCount" class="count">{{ upvotes }}</span>
    </button>

    <!-- 点踩按钮 -->
    <button
      :class="['vote-btn', 'downvote', { active: userVote === -1 }]"
      @click="() => handleVote(-1)"
      :disabled="loading"
      :title="userVote === -1 ? '取消点踩' : '点踩'"
    >
      <ThumbsDown :size="iconSize" :class="{ 'icon-spin': loading && userVote === -1 }" />
      <span v-if="showCount" class="count">{{ downvotes }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { ThumbsUp, ThumbsDown } from 'lucide-vue-next'
import { useVote, type VoteState } from '@/composables/useVote'

interface Props {
  targetType: 'post' | 'comment'
  targetId: number
  upvotes: number
  downvotes: number
  userVote: 1 | -1 | 0
  showCount?: boolean
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  showCount: true,
  iconSize: 16
})

const emit = defineEmits<{
  voteChange: [state: VoteState]
  loadingChange: [loading: boolean]
}>()

// 使用投票 composable
const { state, upvotes, downvotes, userVote, loading, handleVote } = useVote({
  targetType: props.targetType,
  targetId: props.targetId,
  initialState: {
    upvotes: props.upvotes,
    downvotes: props.downvotes,
    userVote: props.userVote
  }
})

// 监听状态变化，向父组件发送事件
watch(state, (newState) => {
  emit('voteChange', newState)
})

// 监听 loading 状态
watch(loading, (newLoading) => {
  emit('loadingChange', newLoading)
})
</script>

<style scoped>
.vote-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
}

.vote-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: background-color 0.2s ease, color 0.2s ease;
  color: #888;
  font-size: 13px;
  font-weight: 500;
  user-select: none;
  height: 32px;
  box-sizing: border-box;
}

.vote-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.vote-btn.upvote.active {
  color: #ff4757;
}

.vote-btn.downvote.active {
  color: #747d8c;
}

.vote-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.count {
  font-size: 12px;
  font-weight: 500;
  min-width: 14px;
  text-align: center;
}

/* 加载动画 */
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(180deg);
  }
}

.icon-spin {
  animation: spin 0.3s ease-in-out;
}

/* 触摸反馈 */
@media (hover: none) {
  .vote-btn:active:not(:disabled) {
    transform: scale(0.95);
  }
}
</style>
