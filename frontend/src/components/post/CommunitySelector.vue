<template>
  <div class="community-selector">
    <div class="selector-trigger" @click="toggleDropdown">
      <div v-if="selectedCommunity" class="selected-community">
        <span class="community-icon">👾</span>
        <span class="community-name">{{ selectedCommunity.name }}</span>
        <span class="member-count">{{ formatCount(selectedCommunity.member_count) }}</span>
      </div>
      <div v-else class="placeholder">
        <span>{{ t('communitySelector.placeholder') }}</span>
      </div>
      <ChevronDown :size="16" class="dropdown-icon" :class="{ active: isOpen }" />
    </div>

    <!-- 下拉菜单 -->
    <div v-if="isOpen" class="dropdown-menu">
      <!-- 搜索框 -->
      <div class="search-box">
        <Search :size="16" class="search-icon" />
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          :placeholder="t('communitySelector.searchPlaceholder')"
          class="search-input"
        />
      </div>

      <!-- 社区列表 -->
      <div class="community-list">
        <div
          v-for="community in filteredCommunities"
          :key="community.id"
          class="community-item"
          :class="{ selected: modelValue === community.id }"
          @click="selectCommunity(community)"
        >
          <div class="community-info">
            <span class="community-icon">👾</span>
            <div class="community-details">
              <div class="community-name">{{ community.name }}</div>
              <div v-if="community.description" class="community-description">
                {{ community.description }}
              </div>
            </div>
          </div>
          <span class="member-count">{{ formatCount(community.member_count) }}</span>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredCommunities.length === 0" class="empty-state">
          <span v-if="loading">{{ t('common.loading') }}</span>
          <span v-else-if="searchQuery">{{ t('communitySelector.noMatch') }}</span>
          <span v-else>{{ t('communitySelector.noCommunities') }}</span>
        </div>
      </div>
    </div>

    <!-- 点击外部关闭 -->
    <div v-if="isOpen" class="overlay" @click="closeDropdown"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ChevronDown, Search } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Number,
    default: null
  },
  communities: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

const isOpen = ref(false)
const searchQuery = ref('')
const searchInput = ref(null)

// 计算属性
const selectedCommunity = computed(() => {
  return props.communities.find(c => c.id === props.modelValue)
})

const filteredCommunities = computed(() => {
  if (!searchQuery.value) {
    return props.communities
  }
  const query = searchQuery.value.toLowerCase()
  return props.communities.filter(c =>
    c.name.toLowerCase().includes(query) ||
    (c.description && c.description.toLowerCase().includes(query))
  )
})

// 格式化数字
const formatCount = (count) => {
  if (count >= 10000) {
    return (count / 10000).toFixed(1) + 'w'
  } else if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'k'
  }
  return count.toString()
}

// 方法
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
}

const selectCommunity = (community) => {
  emit('update:modelValue', community.id)
  closeDropdown()
}

// 监听搜索输入（防抖）
let searchTimeout
watch(searchQuery, (newVal) => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    emit('search', newVal)
  }, 300)
})
</script>

<style scoped>
.community-selector {
  position: relative;
}

.selector-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border: 2px solid #edeff1;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 48px;
}

.selector-trigger:hover {
  border-color: #0079d3;
}

.selector-trigger:focus-within {
  border-color: #0079d3;
  box-shadow: 0 0 0 3px rgba(0, 121, 211, 0.1);
}

.selected-community {
  display: flex;
  align-items: center;
  gap: 10px;
}

.placeholder {
  color: #878a8c;
}

.community-name {
  font-weight: 600;
  color: #1c1c1c;
}

.member-count {
  font-size: 12px;
  color: #878a8c;
  background: #f6f7f8;
  padding: 2px 8px;
  border-radius: 12px;
}

.dropdown-icon {
  color: #878a8c;
  transition: transform 0.2s;
}

.dropdown-icon.active {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #edeff1;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.search-box {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #edeff1;
  gap: 8px;
  background: #f6f7f8;
  border-radius: 8px 8px 0 0;
}

.search-icon {
  color: #878a8c;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: #1c1c1c;
}

.search-input::placeholder {
  color: #878a8c;
}

.community-list {
  overflow-y: auto;
  max-height: 300px;
}

.community-list::-webkit-scrollbar {
  width: 6px;
}

.community-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.community-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f6f7f8;
}

.community-item:last-child {
  border-bottom: none;
}

.community-item:hover {
  background: #f6f7f8;
}

.community-item.selected {
  background: #e5f3fa;
}

.community-info {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0;
}

.community-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.community-details {
  flex: 1;
  min-width: 0;
}

.community-name {
  font-weight: 600;
  color: #1c1c1c;
  font-size: 14px;
}

.community-description {
  font-size: 12px;
  color: #878a8c;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: #878a8c;
  font-size: 14px;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

/* 响应式 */
@media (max-width: 639px) {
  .dropdown-menu {
    max-height: 350px;
  }

  .community-list {
    max-height: 250px;
  }
}
</style>
