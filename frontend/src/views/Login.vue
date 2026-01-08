<template>
  <div class="login-container">
    <div class="login-card">
      

      <div class="card-header">
        <h2 class="title">{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
        <p class="subtitle">SUPER</p>
      </div>

   
      <form @submit.prevent="handleSubmit" class="form-body">
        
   
        <div class="input-group">
          <input 
            type="text" 
            v-model="form.username" 
            placeholder="用户名 / 邮箱" 
            required
          />
        </div>

    
        <div class="input-group">
          <input 
            type="password" 
            v-model="form.password" 
            placeholder="密码" 
            required
          />
        </div>

        <div class="input-group" v-if="!isLogin">
          <input 
            type="password" 
            v-model="form.confirmPassword" 
            placeholder="确认密码" 
            required
          />
        </div>


        <button type="submit" class="submit-btn">
          {{ isLogin ? '登 录' : '注 册' }}
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

const router = useRouter();

// 状态控制：true为登录，false为注册
const isLogin = ref(true);

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
const handleSubmit = () => {
  if (isLogin.value) {
    // TODO: 调用登录接口
    console.log('执行登录', form);
    router.push('/'); 
  } else {

    if (form.password !== form.confirmPassword) {
      alert("两次输入的密码不一致");
      return;
    }
    console.log('执行注册', form);
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