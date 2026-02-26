<template>
  <div class="file-uploader">
    <el-upload
      ref="uploadRef"
      :action="uploadUrl"
      :headers="uploadHeaders"
      :http-request="customRequest"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :file-list="internalFileList"
      :accept="acceptTypes"
      :multiple="multiple"
      :limit="limit"
      :auto-upload="autoUpload"
      :drag="drag"
      name="files"
      list-type="picture-card"
      class="upload-component"
    >
      <template #default>
        <div class="upload-trigger">
          <el-icon :size="24"><Plus /></el-icon>
          <div class="upload-text">上传文件</div>
        </div>
      </template>

      <template #file="{ file }">
        <div class="upload-file-item">
          <img
            v-if="isImage(file)"
            :src="file.url"
            class="upload-preview"
          />
          <div v-else class="upload-file-icon">
            <el-icon :size="32"><Document /></el-icon>
          </div>
          <div class="upload-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatSize(file.size || file.raw?.size) }}</span>
          </div>
          <div class="upload-actions">
            <el-icon
              :size="16"
              class="action-btn view-btn"
              @click="handlePreview(file)"
            >
              <View />
            </el-icon>
            <el-icon
              :size="16"
              class="action-btn delete-btn"
              @click="handleRemove(file)"
            >
              <Delete />
            </el-icon>
          </div>
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, Document, View, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  // 上传类型: image/video/file/mixed
  uploadType: {
    type: String,
    default: 'mixed',
    validator: (val) => ['image', 'video', 'file', 'mixed'].includes(val)
  },
  // 最大文件数量
  limit: {
    type: Number,
    default: 10
  },
  // 是否允许多选
  multiple: {
    type: Boolean,
    default: true
  },
  // 是否自动上传
  autoUpload: {
    type: Boolean,
    default: true
  },
  // 是否支持拖拽
  drag: {
    type: Boolean,
    default: true
  },
  // 外部传入的文件列表
  fileList: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:fileList', 'upload-success', 'upload-progress'])

const uploadRef = ref(null)
const internalFileList = ref([])

// 监听外部 fileList 变化
watch(() => props.fileList, (newVal) => {
  internalFileList.value = [...newVal]
}, { immediate: true })

// 根据上传类型选择 API 端点
const uploadUrl = computed(() => {
  const baseUrl = '/api/v1/uploads'
  switch (props.uploadType) {
    case 'image':
      return `${baseUrl}/images`
    case 'video':
      return `${baseUrl}/videos`
    case 'file':
      return `${baseUrl}/files`
    case 'mixed':
    default:
      return `${baseUrl}/batch`
  }
})

// 接受的文件类型
const acceptTypes = computed(() => {
  switch (props.uploadType) {
    case 'image':
      return 'image/*'
    case 'video':
      return 'video/*'
    case 'file':
      return '*'
    case 'mixed':
    default:
      return 'image/*,video/*,*'
  }
})

// 上传请求头(包含认证 Token)
const uploadHeaders = computed(() => {
  const tokenStr = localStorage.getItem('token')
  if (!tokenStr) return {}

  try {
    // token 是 JSON 字符串格式
    const token = JSON.parse(tokenStr)
    return {
      'Authorization': `Bearer ${token}`
    }
  } catch {
    return {}
  }
})

// 判断是否为图片
const isImage = (file) => {
  const mimeType = file.raw?.type || file.type
  return mimeType?.startsWith('image/')
}

// 格式化文件大小
const formatSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 获取最大文件大小
const getMaxSize = (mimeType) => {
  if (mimeType?.startsWith('image/')) {
    return 10 * 1024 * 1024 // 10MB
  } else if (mimeType?.startsWith('video/')) {
    return 100 * 1024 * 1024 // 100MB
  } else {
    return 50 * 1024 * 1024 // 50MB
  }
}

// 上传前校验
const beforeUpload = (file) => {
  // 发出上传进度事件
  emit('upload-progress')
  // 文件大小校验
  const maxSize = getMaxSize(file.type)
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${formatSize(maxSize)}`)
    return false
  }
  return true
}

// 自定义上传方法
const customRequest = async (options) => {
  const { file, onSuccess, onError } = options

  console.log('[FileUploader] 开始上传:', file.name)

  try {
    // 创建 FormData
    const formData = new FormData()
    formData.append('files', file)

    // 使用 fetch 上传
    const response = await fetch(uploadUrl.value, {
      method: 'POST',
      headers: uploadHeaders.value,
      body: formData
    })

    if (!response.ok) {
      throw new Error(`上传失败: ${response.statusText}`)
    }

    const result = await response.json()
    console.log('[FileUploader] 上传成功响应:', result)

    // 处理响应
    const uploadedFiles = Array.isArray(result) ? result : [result]

    // 更新 internalFileList
    uploadedFiles.forEach(item => {
      // 检查是否已存在
      const exists = internalFileList.value.some(f => f.name === item.file_name)
      if (!exists) {
        internalFileList.value.push({
          name: item.file_name,
          url: item.file_url,
          size: item.file_size,
          type: item.mime_type,
          attachmentType: item.attachment_type,
          attachmentId: item.id,
          raw: file,
          status: 'success'
        })
      }
    })

    emit('update:fileList', internalFileList.value)

    // 调用成功回调
    onSuccess(result, file)

    // 检查是否所有文件都上传完成
    const allDone = internalFileList.value.every(f => f.status === 'success')
    if (allDone && internalFileList.value.length > 0) {
      emit('upload-success')
    }

    ElMessage.success('上传成功')
  } catch (error) {
    console.error('[FileUploader] 上传错误:', error)
    onError(error)
    ElMessage.error('上传失败: ' + error.message)
  }
}

// 文件状态改变
const handleChange = (_, fileList) => {
  // 检查是否所有文件都上传完成
  const allDone = fileList.every(f => f.status === 'success')
  if (allDone && fileList.length > 0) {
    emit('upload-success')
  }
}

// 上传成功
const handleSuccess = (response, file) => {
  console.log('[FileUploader] 上传成功', { response, fileName: file.name, responseType: typeof response })

  // 如果是批量上传，response 是数组
  const uploadedFiles = Array.isArray(response) ? response : [response]
  console.log('[FileUploader] 处理上传文件:', uploadedFiles)

  uploadedFiles.forEach(item => {
    internalFileList.value.push({
      name: item.file_name,
      url: item.file_url,
      size: item.file_size,
      type: item.mime_type,
      attachmentType: item.attachment_type,
      attachmentId: item.id,
      raw: file,
      status: 'success'
    })
  })

  console.log('[FileUploader] internalFileList:', internalFileList.value)
  ElMessage.success('上传成功')
  emit('update:fileList', internalFileList.value)
  emit('upload-success', uploadedFiles)
}

// 上传失败
const handleError = (error, file) => {
  console.error('[FileUploader] 上传失败', { error, fileName: file.name })
  ElMessage.error('上传失败: ' + error.message)
}

// 移除文件
const handleRemove = (file) => {
  const index = internalFileList.value.findIndex(f => f.url === file.url)
  if (index > -1) {
    internalFileList.value.splice(index, 1)
    emit('update:fileList', internalFileList.value)
  }
}

// 预览文件
const handlePreview = (file) => {
  window.open(file.url, '_blank')
}

// 暴露方法给父组件
defineExpose({
  clearFiles: () => {
    internalFileList.value = []
    uploadRef.value?.clearFiles()
  },
  submitUpload: () => {
    uploadRef.value?.submit()
  },
  getAttachmentIds: () => {
    return internalFileList.value
      .filter(f => f.attachmentId)
      .map(f => f.attachmentId)
  }
})
</script>

<style scoped>
.file-uploader {
  width: 100%;
}

.upload-component {
  width: 100%;
}

.upload-trigger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  cursor: pointer;
}

.upload-text {
  margin-top: 8px;
  font-size: 14px;
  color: #878a8c;
}

.upload-file-item {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upload-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-file-icon {
  color: #878a8c;
}

.upload-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  font-size: 12px;
}

.file-name {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  display: block;
  opacity: 0.8;
}

.upload-actions {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.upload-file-item:hover .upload-actions {
  opacity: 1;
}

.action-btn {
  cursor: pointer;
  color: white;
  background: rgba(0, 0, 0, 0.5);
  padding: 8px;
  border-radius: 4px;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

.delete-btn {
  color: #ff4500;
}
</style>
