<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('passwordEditDialog.title')"
    width="450px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
      <el-form-item :label="$t('passwordEditDialog.oldPasswordLabel')" prop="old_password">
        <el-input
          v-model="form.old_password"
          type="password"
          :placeholder="$t('passwordEditDialog.oldPasswordPlaceholder')"
          show-password
        />
      </el-form-item>

      <el-form-item :label="$t('passwordEditDialog.newPasswordLabel')" prop="new_password">
        <el-input
          v-model="form.new_password"
          type="password"
          :placeholder="$t('passwordEditDialog.newPasswordPlaceholder')"
          show-password
        />
      </el-form-item>

      <el-form-item :label="$t('passwordEditDialog.confirmPasswordLabel')" prop="confirm_password">
        <el-input
          v-model="form.confirm_password"
          type="password"
          :placeholder="$t('passwordEditDialog.confirmPasswordPlaceholder')"
          show-password
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">{{ $t('passwordEditDialog.cancel') }}</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ $t('passwordEditDialog.confirmChange') }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'success'])

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 自定义验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.new_password) {
    callback(new Error(t('passwordEditDialog.passwordMismatch')))
  } else {
    callback()
  }
}

const rules = computed(() => ({
  old_password: [
    { required: true, message: t('passwordEditDialog.oldPasswordRequired'), trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: t('passwordEditDialog.newPasswordRequired'), trigger: 'blur' },
    { min: 6, max: 30, message: t('passwordEditDialog.passwordLength'), trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: t('passwordEditDialog.confirmPasswordRequired'), trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}))

const getAuthHeaders = () => {
  const tokenStr = localStorage.getItem('token')
  if (!tokenStr) return {}
  try {
    const token = JSON.parse(tokenStr)
    return { 'Authorization': `Bearer ${token}` }
  } catch {
    return {}
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const response = await fetch('/api/v1/users/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders()
        },
        body: JSON.stringify({
          old_password: form.old_password,
          new_password: form.new_password
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || t('passwordEditDialog.changeFailed'))
      }

      ElMessage.success(t('passwordEditDialog.changeSuccess'))
      emit('success')
      dialogVisible.value = false

      // 清空表单
      form.old_password = ''
      form.new_password = ''
      form.confirm_password = ''
    } catch (error) {
      console.error('修改密码失败:', error)
      ElMessage.error(error.message || t('passwordEditDialog.changeFailed'))
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
