<template>
  <div class="markdown-editor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <button
        v-for="tool in tools"
        :key="tool.name"
        type="button"
        class="toolbar-btn"
        :title="tool.title"
        @click="executeTool(tool.action)"
      >
        <component :is="tool.icon" :size="16" />
      </button>

      <div class="toolbar-divider"></div>

      <button
        type="button"
        class="toolbar-btn"
        :class="{ active: showPreview }"
        :title="t('markdownEditor.togglePreview')"
        @click="togglePreview"
      >
        <Eye :size="16" />
      </button>
    </div>

    <!-- 编辑区域 -->
    <div class="editor-container" :class="{ 'preview-mode': showPreview }">
      <!-- 输入框 -->
      <div v-show="!showPreview || !showPreviewOnly" class="editor-input-wrapper">
        <textarea
          ref="textareaRef"
          v-model="content"
          class="editor-textarea"
          :placeholder="t('markdownEditor.placeholder')"
          @input="handleInput"
          @scroll="syncScroll"
        ></textarea>
      </div>

      <!-- 预览 -->
      <div v-show="showPreview" class="editor-preview-wrapper" ref="previewRef">
        <div class="editor-preview" v-html="renderedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Bold,
  Italic,
  Link,
  Code,
  List,
  ListOrdered,
  Quote,
  Heading1,
  Heading2,
  Eye
} from 'lucide-vue-next'
import { marked } from 'marked'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  showPreviewOnly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const { t } = useI18n()

const content = ref(props.modelValue)
const showPreview = ref(false)
const textareaRef = ref(null)
const previewRef = ref(null)

// 工具栏配置
const tools = computed(() => [
  { name: 'bold', title: t('markdownEditor.boldTitle'), icon: Bold, action: 'bold' },
  { name: 'italic', title: t('markdownEditor.italicTitle'), icon: Italic, action: 'italic' },
  { name: 'link', title: t('markdownEditor.linkTitle'), icon: Link, action: 'link' },
  { name: 'code', title: t('markdownEditor.codeTitle'), icon: Code, action: 'code' },
  { name: 'heading1', title: t('markdownEditor.heading1Title'), icon: Heading1, action: 'h1' },
  { name: 'heading2', title: t('markdownEditor.heading2Title'), icon: Heading2, action: 'h2' },
  { name: 'quote', title: t('markdownEditor.quoteTitle'), icon: Quote, action: 'quote' },
  { name: 'list', title: t('markdownEditor.unorderedListTitle'), icon: List, action: 'ul' },
  { name: 'orderedList', title: t('markdownEditor.orderedListTitle'), icon: ListOrdered, action: 'ol' },
])

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

// 渲染 Markdown
const renderedContent = computed(() => {
  if (!content.value) return `<p class="empty-placeholder">${t('markdownEditor.previewPlaceholder')}</p>`
  try {
    return marked(content.value)
  } catch (error) {
    console.error('Markdown 渲染错误:', error)
    return `<p class="error">${t('markdownEditor.renderError')}</p>`
  }
})

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal
  }
})

// 监听内部值变化
watch(content, (newVal) => {
  emit('update:modelValue', newVal)
})

// 处理输入
const handleInput = () => {
  // 可以在这里添加实时保存逻辑
}

// 同步滚动
const syncScroll = (e) => {
  if (!showPreview.value || !previewRef.value) return

  const textarea = e.target
  const preview = previewRef.value

  const percentage = textarea.scrollTop / (textarea.scrollHeight - textarea.clientHeight)
  preview.scrollTop = percentage * (preview.scrollHeight - preview.clientHeight)
}

// 执行工具栏操作
const executeTool = (action) => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  let replacement = ''
  let cursorOffset = 0

  switch (action) {
    case 'bold':
      replacement = `**${selectedText || t('markdownEditor.boldText')}**`
      cursorOffset = selectedText ? replacement.length : 2
      break
    case 'italic':
      replacement = `*${selectedText || t('markdownEditor.italicText')}*`
      cursorOffset = selectedText ? replacement.length : 1
      break
    case 'link':
      replacement = `[${selectedText || t('markdownEditor.linkText')}](url)`
      cursorOffset = selectedText ? replacement.length - 4 : 1
      break
    case 'code':
      replacement = `\`${selectedText || t('markdownEditor.codeText')}\``
      cursorOffset = selectedText ? replacement.length : 1
      break
    case 'h1':
      replacement = `# ${selectedText || t('markdownEditor.heading1Text')}`
      cursorOffset = replacement.length
      break
    case 'h2':
      replacement = `## ${selectedText || t('markdownEditor.heading2Text')}`
      cursorOffset = replacement.length
      break
    case 'quote':
      replacement = `> ${selectedText || t('markdownEditor.quoteText')}`
      cursorOffset = replacement.length
      break
    case 'ul':
      replacement = `- ${selectedText || t('markdownEditor.listItemText')}`
      cursorOffset = replacement.length
      break
    case 'ol':
      replacement = `1. ${selectedText || t('markdownEditor.listItemText')}`
      cursorOffset = replacement.length
      break
  }

  content.value =
    content.value.substring(0, start) + replacement + content.value.substring(end)

  // 设置光标位置
  nextTick(() => {
    const newPosition = start + cursorOffset
    textarea.setSelectionRange(newPosition, newPosition)
    textarea.focus()
  })
}

// 切换预览
const togglePreview = () => {
  showPreview.value = !showPreview.value
}

// 暴露方法
defineExpose({
  focus: () => textareaRef.value?.focus()
})
</script>

<style scoped>
.markdown-editor {
  border: 2px solid #edeff1;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.markdown-editor:focus-within {
  border-color: #0079d3;
}

.toolbar {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: #f6f7f8;
  border-bottom: 1px solid #edeff1;
  gap: 4px;
  flex-wrap: wrap;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #878a8c;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.15s;
}

.toolbar-btn:hover {
  background: #edeff1;
  color: #1c1c1c;
}

.toolbar-btn.active {
  background: #0079d3;
  color: var(--text-inverse);
}

.toolbar-divider {
  width: 1px;
  height: 20px;
  background: #edeff1;
  margin: 0 4px;
}

.editor-container {
  display: flex;
  min-height: 300px;
  background: var(--bg-card);
}

.editor-container.preview-mode {
  min-height: 400px;
}

.editor-input-wrapper,
.editor-preview-wrapper {
  flex: 1;
  overflow: auto;
}

.editor-input-wrapper {
  border-right: 1px solid #edeff1;
}

.editor-textarea {
  width: 100%;
  min-height: 300px;
  padding: 16px;
  border: none;
  outline: none;
  resize: vertical;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #1c1c1c;
  background: var(--bg-card);
}

.editor-textarea::placeholder {
  color: #878a8c;
}

.editor-preview-wrapper {
  padding: 16px;
  background: var(--bg-card);
  overflow-y: auto;
}

.editor-preview {
  line-height: 1.6;
  color: #1c1c1c;
}

/* Markdown 样式 */
.editor-preview :deep(h1) {
  font-size: 2em;
  font-weight: 600;
  margin: 0.67em 0;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #edeff1;
}

.editor-preview :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 0.75em 0;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #edeff1;
}

.editor-preview :deep(p) {
  margin: 0 0 16px 0;
}

.editor-preview :deep(code) {
  background: #f6f7f8;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.editor-preview :deep(pre) {
  background: #f6f7f8;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0 0 16px 0;
}

.editor-preview :deep(pre code) {
  background: transparent;
  padding: 0;
}

.editor-preview :deep(blockquote) {
  border-left: 4px solid #0079d3;
  padding-left: 16px;
  margin: 0 0 16px 0;
  color: #878a8c;
}

.editor-preview :deep(ul),
.editor-preview :deep(ol) {
  margin: 0 0 16px 0;
  padding-left: 24px;
}

.editor-preview :deep(li) {
  margin: 4px 0;
}

.editor-preview :deep(a) {
  color: #0079d3;
  text-decoration: none;
}

.editor-preview :deep(a:hover) {
  text-decoration: underline;
}

.editor-preview :deep(img) {
  max-width: 100%;
  height: auto;
}

.empty-placeholder {
  color: #878a8c;
  font-style: italic;
}

.error {
  color: #ff4500;
}

/* 响应式 */
@media (max-width: 639px) {
  .editor-container.preview-mode {
    flex-direction: column;
  }

  .editor-input-wrapper {
    border-right: none;
    border-bottom: 1px solid #edeff1;
    max-height: 200px;
  }

  .editor-preview-wrapper {
    max-height: 200px;
  }

  .toolbar {
    gap: 2px;
  }

  .toolbar-btn {
    width: 28px;
    height: 28px;
  }
}
</style>
