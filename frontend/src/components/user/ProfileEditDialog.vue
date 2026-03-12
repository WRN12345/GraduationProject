<template>
  <el-dialog
    v-model="dialogVisible"
    title="编辑个人资料"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <!-- 头像编辑 -->
      <el-form-item label="头像">
        <div class="avatar-upload">
          <el-upload
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            accept="image/*"
          >
            <img v-if="form.avatar" :src="form.avatar" class="avatar-preview" />
            <div v-else class="avatar-uploader-icon">
              <Plus :size="28" />
            </div>
          </el-upload>
          <div class="avatar-tip">支持 JPG、PNG 格式,最大 5MB</div>
        </div>
      </el-form-item>

      <!-- 用户名 -->
      <el-form-item label="用户名" prop="username">
        <el-input v-model="form.username" placeholder="3-20个字符" />
      </el-form-item>

      <!-- 昵称 -->
      <el-form-item label="昵称" prop="nickname">
        <el-input v-model="form.nickname" placeholder="显示名称" />
      </el-form-item>

      <!-- 邮箱 -->
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" type="email" placeholder="your@email.com" />
      </el-form-item>

      <!-- 个人简介 -->
      <el-form-item label="个人简介" prop="bio">
        <el-input
          v-model="form.bio"
          type="textarea"
          :rows="3"
          maxlength="5000"
          show-word-limit
          placeholder="介绍一下自己..."
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          保存
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: Boolean,
  user: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  nickname: '',
  email: '',
  bio: '',
  avatar: ''
})

// 监听 user prop 变化
watch(() => props.user, (newUser) => {
  if (newUser) {
    Object.assign(form, {
      username: newUser.username || '',
      nickname: newUser.nickname || '',
      email: newUser.email || '',
      bio: newUser.bio || '',
      avatar: newUser.avatar || ''
    })
  }
}, { immediate: true })

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
  ],
  nickname: [
    { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 上传配置
const uploadUrl = computed(() => '/api/v1/users/avatar')

const uploadHeaders = computed(() => {
  const tokenStr = localStorage.getItem('token')
  if (!tokenStr) return {}
  try {
    const token = JSON.parse(tokenStr)
    return { 'Authorization': `Bearer ${token}` }
  } catch {
    return {}
  }
})

// 头像上传前验证
const beforeAvatarUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('头像大小不能超过 5MB!')
    return false
  }
  return true
}

// 头像上传成功
const handleAvatarSuccess = (response) => {
  form.avatar = response.avatar_url
  ElMessage.success('头像上传成功')
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      // 先更新用户名(如果改变了)
      if (form.username !== props.user.username) {
        const usernameResponse = await fetch('/api/v1/users/username', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            ...uploadHeaders.value
          },
          body: JSON.stringify({ username: form.username })
        })

        if (!usernameResponse.ok) {
          const error = await usernameResponse.json()
          throw new Error(error.detail || '用户名修改失败')
        }
      }

      // 更新其他资料
      const profileResponse = await fetch('/api/v1/users/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...uploadHeaders.value
        },
        body: JSON.stringify({
          nickname: form.nickname,
          email: form.email,
          bio: form.bio,
          avatar: form.avatar
        })
      })

      if (!profileResponse.ok) {
        const error = await profileResponse.json()
        throw new Error(error.detail || '资料更新失败')
      }

      ElMessage.success('个人资料更新成功')
      emit('success')
      dialogVisible.value = false
    } catch (error) {
      console.error('更新个人资料失败:', error)
      ElMessage.error(error.message || '更新失败，请重试')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e4e7ed;
  cursor: pointer;
}

.avatar-uploader-icon {
  width: 80px;
  height: 80px;
  border: 1px dashed #d9d9d9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #8c939d;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
  color: #409eff;
}

.avatar-tip {
  font-size: 12px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
