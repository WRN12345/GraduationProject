<template>
  <div class="login-container">
    <div class="login-card">
      

      <div class="card-header">
        <Shield :size="40" class="header-icon" />
        <h2 class="title">{{ pageTitle }}</h2>
        <p class="subtitle">SUPER</p>
      </div>

   
      <form @submit.prevent="handleSubmit" class="form-body">
        
   
        <div class="input-wrapper">
          <User :size="20" class="input-icon" />
          <input
            type="text"
            v-model="form.username"
            :placeholder="t('login.usernamePlaceholder')"
          />
        </div>

    
        <div class="input-wrapper">
          <Lock :size="20" class="input-icon" />
          <input
            type="password"
            v-model="form.password"
            :placeholder="t('login.passwordPlaceholder')"
          />
        </div>

        <div class="input-wrapper" v-if="mode !== 'login'">
          <Lock :size="20" class="input-icon" />
          <input
            type="password"
            v-model="form.confirmPassword"
            :placeholder="t('login.confirmPasswordPlaceholder')"
          />
        </div>

        <!-- 管理员注册额外字段 -->
        <template v-if="mode === 'adminRegister'">
          <div class="input-wrapper">
            <User :size="20" class="input-icon" />
            <input
              type="text"
              v-model="form.nickname"
              :placeholder="t('login.nicknamePlaceholder')"
            />
          </div>

          <div class="input-wrapper">
            <Mail :size="20" class="input-icon" />
            <input
              type="email"
              v-model="form.email"
              :placeholder="t('login.emailPlaceholder')"
            />
          </div>

          <div class="input-wrapper">
            <Key :size="20" class="input-icon" />
            <input
              type="password"
              v-model="form.adminRegisterKey"
              :placeholder="t('login.adminKeyPlaceholder')"
            />
          </div>
        </template>


        <button type="submit" class="submit-btn" :disabled="isLoading">
          <component :is="mode === 'login' ? LogIn : UserPlus" :size="18" class="btn-icon" />
          {{ isLoading ? t('login.processing') : submitButtonText }}
        </button>
      </form>

      <div class="card-footer">
        <p v-if="mode === 'login'">
          {{ t('login.noAccount') }}
          <span @click="switchMode('register')" class="link">{{ t('login.registerNow') }}</span>
        </p>
        <p v-else-if="mode === 'register'">
          {{ t('login.hasAccount') }}
          <span @click="switchMode('login')" class="link">{{ t('login.loginDirectly') }}</span>
          <span class="separator">|</span>
          <span @click="switchMode('adminRegister')" class="link">{{ t('login.registerAdminNow') }}</span>
        </p>
        <p v-else>
          {{ t('login.hasAccount') }}
          <span @click="switchMode('login')" class="link">{{ t('login.loginDirectly') }}</span>
          <span class="separator">|</span>
          <span @click="switchMode('register')" class="link">{{ t('login.backToRegister') }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { User, Lock, LogIn, UserPlus, Shield, Key, Mail } from 'lucide-vue-next';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/stores/user';
import { useThemeStore } from '@/stores/theme';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

// 登录页面强制使用浅色主题，离开时恢复
const themeStore = useThemeStore();
let wasDark = false;

onMounted(() => {
  wasDark = themeStore.isDark;
  if (wasDark) {
    themeStore.isDark = false;
  }
});

onBeforeUnmount(() => {
  if (wasDark) {
    themeStore.isDark = true;
  }
});

const router = useRouter();
const userStore = useUserStore();

// 模式控制：'login' | 'register' | 'adminRegister'
const mode = ref('login');
// 加载状态
const isLoading = ref(false);

// 表单数据
const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  nickname: '',
  email: '',
  adminRegisterKey: ''
});

// 页面标题
const pageTitle = computed(() => {
  if (mode.value === 'login') return t('login.welcomeBack');
  if (mode.value === 'register') return t('login.createAccount');
  return t('login.adminRegisterTitle');
});

// 提交按钮文字
const submitButtonText = computed(() => {
  if (mode.value === 'login') return t('login.login');
  if (mode.value === 'register') return t('login.register');
  return t('login.adminRegisterTitle');
});

// 切换模式
const switchMode = (newMode) => {
  mode.value = newMode;
  form.password = '';
  form.confirmPassword = '';
};

// 提交处理
const handleSubmit = async () => {
  console.log('[Login] 表单提交:', {
    mode: mode.value,
    username: form.username,
    passwordLength: form.password?.length
  })

  if (isLoading.value) return;

  // 基本验证
  if (!form.username.trim()) {
    ElMessage.error(t('login.enterUsername'));
    return;
  }

  if (!form.password) {
    ElMessage.error(t('login.enterPassword'));
    return;
  }

  // 注册和管理员注册模式下验证
  if (mode.value !== 'login') {
    // 用户名长度验证
    const username = form.username.trim()
    if (username.length < 3 || username.length > 20) {
      ElMessage.error(t('login.usernameLengthError'));
      return;
    }

    // 密码长度验证
    if (form.password.length < 6 || form.password.length > 30) {
      ElMessage.error(t('login.passwordLengthError'));
      return;
    }

    if (!form.confirmPassword) {
      ElMessage.error(t('login.confirmPassword'));
      return;
    }
    if (form.password !== form.confirmPassword) {
      ElMessage.error(t('login.passwordMismatch'));
      return;
    }
  }

  // 管理员注册模式下验证密钥和邮箱
  if (mode.value === 'adminRegister') {
    if (!form.adminRegisterKey.trim()) {
      ElMessage.error(t('login.enterAdminKey'));
      return;
    }
    // 邮箱格式验证（如果填写了）
    if (form.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
      ElMessage.error(t('login.invalidEmail'));
      return;
    }
  }

  isLoading.value = true;
  try {
    if (mode.value === 'login') {
      console.log('[Login] 开始登录流程')
      // 登录
      await userStore.login(form.username, form.password);
      console.log('[Login] 登录成功，当前用户信息:', {
        isSuperuser: userStore.isSuperuser,
        isAdmin: userStore.isAdmin,
        isLoggedIn: userStore.isLoggedIn
      })
      // 根据用户角色跳转到对应主页（使用 store 中已保存的状态）
      if (userStore.isSuperuser) {
        console.log('[Login] 超级管理员，跳转到管理后台')
        router.push('/admin');
      } else {
        console.log('[Login] 普通用户，跳转到首页')
        router.push('/');
      }
    } else if (mode.value === 'register') {
      console.log('[Login] 开始注册流程')
      // 普通注册
      const result = await userStore.register(form.username, form.password, form.username);
      console.log('[Login] 注册成功:', result);
      ElMessage.success(t('login.registerSuccess'));
      switchMode('login');
    } else if (mode.value === 'adminRegister') {
      console.log('[Login] 开始管理员注册流程')
      // 管理员注册
      const result = await userStore.registerAdmin(
        form.username,
        form.password,
        form.nickname || undefined,
        form.email || undefined,
        form.adminRegisterKey
      );
      console.log('[Login] 管理员注册成功:', result);
      ElMessage.success(t('login.adminRegisterSuccess'));
      switchMode('login');
    }
  } catch (error) {
    // 错误已由 API 拦截器处理
    console.error('[Login] 认证失败:', error);
  } finally {
    isLoading.value = false;
    console.log('[Login] 流程结束，loading 已重置')
  }
};
</script>

<style scoped>

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ffffff;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  color: #1a1a1a;
  margin-bottom: 12px;
}

.title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  color: #999;
}

.input-group {
  margin-bottom: 20px;
}

.input-wrapper {
  position: relative;
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  pointer-events: none;
}


input {
  width: 100%;
  padding: 14px 16px;
  font-size: 14px;
  border: none;
  background-color: #f7f9fc;
  border-radius: 8px;
  color: #333;
  outline: none;
  transition: background-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.input-wrapper input {
  padding-left: 44px;
}

input:focus {
  background-color: #ffffff;
  box-shadow: 0 0 0 2px #e8eaf0;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #1a1a1a;
  color: var(--text-inverse);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-icon {
  flex-shrink: 0;
}

.submit-btn:hover {
  opacity: 0.9;
}

.card-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.link {
  color: #1a1a1a;
  font-weight: 600;
  cursor: pointer;
  margin-left: 4px;
}

.link:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 8px;
  color: #ccc;
}

.form-body {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
