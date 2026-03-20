<template>
  <button
    :class="['bookmark-btn', { active: isBookmarked, loading }]"
    @click.stop="toggleBookmark"
    :disabled="loading"
    :title="isBookmarked ? '取消收藏' : '收藏'"
  >
    <Star
      :size="iconSize"
      :fill="isBookmarked ? 'currentColor' : 'none'"
      :class="{ 'icon-pop': !loading && isBookmarked }"
    />
    <span v-if="showCount && bookmarkCount > 0" class="count">{{ bookmarkCount }}</span>
  </button>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { Star } from 'lucide-vue-next'
import { useBookmark } from '@/composables/useBookmark'

interface Props {
  postId: number
  bookmarked?: boolean
  count?: number
  showCount?: boolean
  iconSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  bookmarked: false,
  count: 0,
  showCount: false,
  iconSize: 18
})

const emit = defineEmits<{
  bookmarkChange: [bookmarked: boolean, count: number]
  loadingChange: [loading: boolean]
}>()

// 使用收藏 composable（使用不同变量名避免与 props 冲突）
const { bookmarked: isBookmarked, count: bookmarkCount, loading, toggleBookmark } = useBookmark({
  postId: props.postId,
  initialBookmarked: props.bookmarked,
  initialCount: props.count
})

// 监听状态变化
watch([isBookmarked, bookmarkCount], () => {
  emit('bookmarkChange', isBookmarked.value, bookmarkCount.value)
})

watch(loading, (newLoading) => {
  emit('loadingChange', newLoading)
})
</script>

<style scoped>
.bookmark-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  background: transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #888;
  font-size: 13px;
  font-weight: 500;
  user-select: none;
}

.bookmark-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.bookmark-btn.active {
  color: #ffa502;
}

.bookmark-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.count {
  font-size: 13px;
  font-weight: 500;
  min-width: 16px;
  text-align: center;
}

/* 收藏动画 */
@keyframes pop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.icon-pop {
  animation: pop 0.3s ease-out;
}

/* 触摸反馈 */
@media (hover: none) {
  .bookmark-btn:active:not(:disabled) {
    transform: scale(0.95);
  }
}
</style>
