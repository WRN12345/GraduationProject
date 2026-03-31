<script setup>
import { FileText, MessageCircle, ThumbsUp, ThumbsDown } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: String,
    default: 'posts'
  },
  postCount: {
    type: Number,
    default: 0
  },
  commentCount: {
    type: Number,
    default: 0
  },
  upvoteCount: {
    type: Number,
    default: 0
  },
  downvoteCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

const tabs = [
  { value: 'posts', label: t('userTabs.posts'), icon: FileText },
  { value: 'comments', label: t('userTabs.comments'), icon: MessageCircle },
  { value: 'upvoted', label: t('userTabs.upvoted'), icon: ThumbsUp },
  { value: 'downvoted', label: t('userTabs.downvoted'), icon: ThumbsDown }
]

const selectTab = (tab) => {
  emit('update:modelValue', tab.value)
}

const getCount = (tabValue) => {
  switch (tabValue) {
    case 'posts': return props.postCount
    case 'comments': return props.commentCount
    case 'upvoted': return props.upvoteCount
    case 'downvoted': return props.downvoteCount
    default: return 0
  }
}

const hasCount = (tabValue) => {
  return getCount(tabValue) > 0
}
</script>

<template>
  <div class="user-tabs">
    <div
      v-for="tab in tabs"
      :key="tab.value"
      :class="['tab-item', { active: modelValue === tab.value }]"
      @click="selectTab(tab)"
    >
      <component :is="tab.icon" :size="18" />
      <span class="tab-label">{{ tab.label }}</span>
      <span :class="['tab-count', { 'has-count': hasCount(tab.value) }]">
        {{ getCount(tab.value) }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.user-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 0 16px 0;
  border-bottom: 1px solid #edeff1;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.user-tabs::-webkit-scrollbar {
  display: none;
}

.user-tabs {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f6f7f8;
  border: none;
  border-radius: 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: #878a8c;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.tab-item:hover {
  background: #edeff1;
  color: #1c1c1c;
}

.tab-item.active {
  background: #0079d3;
  color: #fff;
}

.tab-label {
  font-size: 14px;
}

.tab-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  color: #878a8c;
}

.tab-count.has-count {
  background: rgba(0, 0, 0, 0.1);
  color: #1c1c1c;
}

.tab-item.active .tab-count {
  background: rgba(255, 255, 255, 0.25);
  color: #fff;
}

/* 响应式 */
@media (max-width: 639px) {
  .user-tabs {
    padding: 12px 0;
    gap: 6px;
  }

  .tab-item {
    padding: 8px 12px;
    font-size: 13px;
  }

  .tab-label {
    font-size: 13px;
  }

  .tab-count {
    min-width: 18px;
    height: 18px;
    font-size: 11px;
    padding: 0 5px;
  }
}
</style>
