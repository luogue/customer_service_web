<template>
  <div class="chat-wrapper">
    <div class="user-info">
      <span>{{ currentUser.name }} ({{ currentUser.role === 'admin' ? '管理员' : '客户' }})</span>
      <div class="user-actions">
        <button v-if="currentUser.role === 'admin'" class="admin-btn" @click="goToAdmin">
          管理后台
        </button>
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>
    </div>
    <ChatComponent :user-role="currentUser.role" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ChatComponent from '../components/ChatComponent.vue'

const router = useRouter()

const currentUser = ref({})

onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    currentUser.value = JSON.parse(savedUser)
  }
})

function goToAdmin() {
  console.log('点击管理后台按钮，准备跳转到 /admin')
  router.push('/admin')
  console.log('跳转完成')
}

function handleLogout() {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/')
}
</script>

<style scoped>
.chat-wrapper {
  width: 100%;
  max-width: 1000px;
  height: 80vh;
  display: flex;
  flex-direction: column;
  margin: 0 auto;
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-radius: 12px 12px 0 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-info span {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.user-actions {
  display: flex;
  gap: 10px;
}

.admin-btn {
  padding: 6px 16px;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  border: none;
  border-radius: 6px;
  font-size: 12px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 179, 71, 0.4);
}

.logout-btn {
  padding: 6px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: #eee;
  border-color: #ccc;
}
</style>
