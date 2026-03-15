<template>
  <button
    :class="['bookmark-btn', { active: bookmarked, loading }]"
    @click.stop="toggleBookmark"
    :disabled="loading"
    :title="bookmarked ? '取消收藏' : '收藏'"
  >
    <Star
      :size="iconSize"
      :fill="bookmarked ? 'currentColor' : 'none'"
      :class="{ 'icon-pop': !loading && bookmarked }"
    />
    <span v-if="showCount && count > 0" class="count">{{ count }}</span>
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

// 使用收藏 composable
const { bookmarked, count, loading, toggleBookmark } = useBookmark({
  postId: props.postId,
  initialBookmarked: props.bookmarked,
  initialCount: props.count
})

// 监听状态变化
watch([bookmarked, count], () => {
  emit('bookmarkChange', bookmarked.value, count.value)
})

watch(loading, (newLoading) => {
  emit('loadingChange', newLoading)
})
</script>

<style scoped>
.bookmark-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border: 1px solid transparent;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  user-select: none;
}

.bookmark-btn:hover:not(:disabled) {
  background: #f8f9fa;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
}

.bookmark-btn.active {
  color: #ffa502;
  background: linear-gradient(135deg, #fff8e1 0%, #ffeaa7 100%);
  border-color: #ffd32a;
}

.bookmark-btn.active:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffeaa7 0%, #ffd980 100%);
}

.bookmark-btn.active svg {
  filter: drop-shadow(0 1px 2px rgba(255, 165, 2, 0.3));
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
