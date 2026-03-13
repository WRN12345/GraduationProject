<template>
  <div class="login-container">
    <div class="login-card">
      

      <div class="card-header">
        <Shield :size="40" class="header-icon" />
        <h2 class="title">{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
        <p class="subtitle">SUPER</p>
      </div>

   
      <form @submit.prevent="handleSubmit" class="form-body">
        
   
        <div class="input-wrapper">
          <User :size="20" class="input-icon" />
          <input
            type="text"
            v-model="form.username"
            placeholder="用户名 / 邮箱"
          />
        </div>

    
        <div class="input-wrapper">
          <Lock :size="20" class="input-icon" />
          <input
            type="password"
            v-model="form.password"
            placeholder="密码"
          />
        </div>

        <div class="input-wrapper" v-if="!isLogin">
          <Lock :size="20" class="input-icon" />
          <input
            type="password"
            v-model="form.confirmPassword"
            placeholder="确认密码"
          />
        </div>


        <button type="submit" class="submit-btn" :disabled="isLoading">
          <component :is="isLogin ? LogIn : UserPlus" :size="18" class="btn-icon" />
          {{ isLoading ? '处理中...' : (isLogin ? '登 录' : '注 册') }}
        </button>
      </form>


      <div class="card-footer">
        <p v-if="isLogin">
          还没有账号？ 
          <span @click="toggleMode" class="link">立即注册</span>
        </p>
        <p v-else>
          已有账号？ 
          <span @click="toggleMode" class="link">直接登录</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { User, Lock, LogIn, UserPlus, Shield } from 'lucide-vue-next';
import { ElMessage } from 'element-plus';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

// 状态控制：true为登录，false为注册
const isLogin = ref(true);
// 加载状态
const isLoading = ref(false);

// 表单数据
const form = reactive({
  username: '',
  password: '',
  confirmPassword: ''
});

// 切换模式
const toggleMode = () => {
  isLogin.value = !isLogin.value;
  form.password = '';
  form.confirmPassword = '';
};

// 提交处理
const handleSubmit = async () => {
  console.log('[Login] 表单提交:', {
    isLogin: isLogin.value,
    username: form.username,
    passwordLength: form.password?.length
  })

  if (isLoading.value) return;

  // 表单验证
  if (!form.username.trim()) {
    ElMessage.error('请输入用户名');
    return;
  }

  if (!form.password) {
    ElMessage.error('请输入密码');
    return;
  }

  // 注册模式下验证密码
  if (!isLogin.value) {
    if (!form.confirmPassword) {
      ElMessage.error('请确认密码');
      return;
    }
    if (form.password !== form.confirmPassword) {
      ElMessage.error('两次输入的密码不一致');
      return;
    }
  }

  isLoading.value = true;
  try {
    if (isLogin.value) {
      console.log('[Login] 开始登录流程')
      // 登录
      await userStore.login(form.username, form.password);
      console.log('[Login] 登录成功，准备跳转到首页')
      router.push('/');
    } else {
      console.log('[Login] 开始注册流程')
      // 注册
      const result = await userStore.register(form.username, form.password, form.username);
      console.log('[Login] 注册成功:', result);
      // 注册成功后切换到登录模式
      ElMessage.success('注册成功，请登录');
      toggleMode();
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
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #ffffff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
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
  background-color: #fff;
  box-shadow: 0 0 0 2px #e8eaf0;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #1a1a1a;
  color: #fff;
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

.form-body {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>