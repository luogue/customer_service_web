<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
          <h2>客服系统登录</h2>
          <p>请输入您的账号密码</p>
        </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="account">手机号/用户名</label>
          <input
            id="account"
            v-model="loginForm.account"
            type="text"
            placeholder="请输入手机号或用户名"
            required
          />
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            required
          />
        </div>
        
        <div class="form-group remember-me">
          <label class="checkbox-label">
            <input
              type="checkbox"
              v-model="loginForm.rememberMe"
            />
            <span>记住密码</span>
          </label>
        </div>
        
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>
        
        <button type="submit" class="login-btn" :disabled="isLoading">
          {{ isLoading ? '登录中..' : '登录' }}
        </button>
      </form>
      
      <div class="login-tips">
        <p>测试账号：</p>
        <p>客户 - 13800000000 / 123456</p>
        <p>管理员 - admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const API_BASE_URL = 'http://localhost:8004'

const emit = defineEmits(['login-success'])

const loginForm = ref({
  account: '',
  password: '',
  rememberMe: false
})

const errorMessage = ref('')
const isLoading = ref(false)

onMounted(() => {
  const savedAccount = localStorage.getItem('saved_account')
  const savedPassword = localStorage.getItem('saved_password')
  if (savedAccount && savedPassword) {
    loginForm.value.account = savedAccount
    loginForm.value.password = atob(savedPassword)
    loginForm.value.rememberMe = true
  }
})

async function handleLogin() {
  errorMessage.value = ''
  
  if (!loginForm.value.account || !loginForm.value.password) {
    errorMessage.value = '请输入手机号/用户名和密码'
    return
  }
  
  // 判断是手机号还是用户名
  const phoneRegex = /^1[3-9]\d{9}$/
  const isPhone = phoneRegex.test(loginForm.value.account)
  const isUsername = loginForm.value.account === 'admin'
  
  isLoading.value = true
  
  try {
    // 构建请求体
    const requestBody = {
      password: loginForm.value.password
    }
    
    if (isUsername) {
      requestBody.username = loginForm.value.account
    } else {
      requestBody.phone = loginForm.value.account
    }
    
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    const data = await response.json()
    
    if (data.success) {
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('token', data.token)
      
      if (loginForm.value.rememberMe) {
        localStorage.setItem('saved_account', loginForm.value.account)
        localStorage.setItem('saved_password', btoa(loginForm.value.password))
      } else {
        localStorage.removeItem('saved_account')
        localStorage.removeItem('saved_password')
      }
      
      // 跳转到聊天页面
      router.push('/chat')
    } else {
      errorMessage.value = data.message
    }
  } catch (error) {
      console.error('登录失败:', error)
      errorMessage.value = '登录失败，请检查网络连接'
    } finally {
      isLoading.value = false
    }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 400px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #ffb347;
}

.error-message {
  color: #f5576c;
  font-size: 14px;
  text-align: center;
  padding: 10px;
  background: #fff5f5;
  border-radius: 8px;
}

.login-btn {
  padding: 14px;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  color: #333;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.remember-me {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.login-tips {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  text-align: center;
}

.login-tips p {
  color: #999;
  font-size: 12px;
  margin: 4px 0;
}
</style>
