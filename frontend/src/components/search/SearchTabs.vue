<script setup>
import { FileText, Users, MessageCircle } from 'lucide-vue-next'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'posts'
  },
  counts: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const tabs = [
  { value: 'posts', label: '帖子', icon: FileText },
  { value: 'users', label: '用户', icon: Users },
  { value: 'comments', label: '评论', icon: MessageCircle }
]

const selectTab = (tab) => {
  emit('update:modelValue', tab.value)
}

const getCount = (tabValue) => {
  return props.counts[tabValue] || 0
}

const hasCount = (tabValue) => {
  return getCount(tabValue) > 0
}
</script>

<template>
  <div class="search-tabs">
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
.search-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 0 16px 0;
  border-bottom: 1px solid #edeff1;
  margin-bottom: 20px;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* 隐藏滚动条 */
.search-tabs::-webkit-scrollbar {
  display: none;
}

.search-tabs {
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
  .search-tabs {
    padding: 12px 0;
    margin-bottom: 16px;
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
