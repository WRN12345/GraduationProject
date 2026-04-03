<template>
  <nav v-if="headings && headings.length > 0" class="toc-container">
    <div class="toc-title">目录</div>
    <ul class="toc-list">
      <li
        v-for="heading in headings"
        :key="heading.id"
        class="toc-item"
        :class="[
          `toc-level-${heading.level}`,
          { active: activeId === heading.id }
        ]"
      >
        <a
          class="toc-link"
          :href="`#${heading.id}`"
          @click.prevent="scrollToHeading(heading.id)"
        >{{ heading.text }}</a>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

const props = defineProps({
  headings: {
    type: Array,
    default: () => []
  }
})

const activeId = ref('')
let observer = null

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const setupObserver = () => {
  // 清理旧的 observer
  if (observer) {
    observer.disconnect()
    observer = null
  }

  if (!props.headings || props.headings.length === 0) return

  // 延迟一帧确保 DOM 已渲染
  requestAnimationFrame(() => {
    const headingElements = props.headings
      .map(h => document.getElementById(h.id))
      .filter(Boolean)

    if (headingElements.length === 0) return

    observer = new IntersectionObserver(
      (entries) => {
        // 找到当前在视口中最靠近顶部的标题
        const visibleEntries = entries.filter(entry => entry.isIntersecting)
        if (visibleEntries.length > 0) {
          // 取最靠近顶部的那个
          const topEntry = visibleEntries.reduce((closest, entry) => {
            return entry.boundingClientRect.top < closest.boundingClientRect.top
              ? entry
              : closest
          })
          activeId.value = topEntry.target.id
        }
      },
      {
        rootMargin: '-80px 0px -60% 0px',
        threshold: 0
      }
    )

    headingElements.forEach(el => {
      observer.observe(el)
    })

    // 初始化时设置第一个可见的标题为 active
    for (const el of headingElements) {
      const rect = el.getBoundingClientRect()
      if (rect.top >= 0 && rect.top <= window.innerHeight * 0.5) {
        activeId.value = el.id
        break
      }
    }
    // 如果没有可见标题，默认激活第一个
    if (!activeId.value && headingElements.length > 0) {
      activeId.value = headingElements[0].id
    }
  })
}

onMounted(() => {
  setupObserver()
})

onBeforeUnmount(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})

// 当 headings 变化时重新设置 observer
watch(() => props.headings, () => {
  activeId.value = ''
  setupObserver()
}, { deep: true })
</script>

<style scoped>
.toc-container {
  width: 250px;
  position: sticky;
  top: 72px;
  max-height: calc(100vh - 88px);
  overflow-y: auto;
  padding: 16px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  flex-shrink: 0;
}

.toc-container::-webkit-scrollbar {
  width: 4px;
}

.toc-container::-webkit-scrollbar-track {
  background: transparent;
}

.toc-container::-webkit-scrollbar-thumb {
  background: var(--border-color, #ddd);
  border-radius: 2px;
}

.toc-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-light, #edeff1);
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin: 0;
  padding: 0;
}

.toc-link {
  display: block;
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s, background-color 0.2s;
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toc-link:hover {
  color: var(--color-primary, #0079d3);
}

.toc-item.active > .toc-link {
  color: var(--color-primary, #0079d3);
  font-weight: 500;
}

/* 层级缩进 */
.toc-level-1 > .toc-link { padding-left: 0; }
.toc-level-2 > .toc-link { padding-left: 12px; }
.toc-level-3 > .toc-link { padding-left: 24px; }
.toc-level-4 > .toc-link { padding-left: 36px; }
.toc-level-5 > .toc-link { padding-left: 48px; }
.toc-level-6 > .toc-link { padding-left: 60px; }

/* 暗色模式适配 */
[data-theme="dark"] .toc-container {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}
</style>
