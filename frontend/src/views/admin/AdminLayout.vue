<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="logo">
        <h3>管理后台</h3>
      </div>
      <nav class="menu">
        <div 
          v-for="item in menuItems" 
          :key="item.key"
          class="menu-item"
          :class="{ active: isActive(item.key) }"
          @click="navigateTo(item.key)"
        >
          <span class="icon">{{ item.icon }}</span>
          <span class="text">{{ item.label }}</span>
        </div>
      </nav>
      <div class="sidebar-footer">
        <button class="btn-back" @click="goBackToChat">
          返回聊天
        </button>
      </div>
    </aside>
    
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuItems = [
  { key: 'model', label: '模型配置', icon: '🤖' },
  { key: 'prompt', label: 'Prompt模板', icon: '📝' },
  { key: 'faq', label: 'FAQ管理', icon: '❓' },
  { key: 'rules', label: '对话规则', icon: '📋' },
  { key: 'transfer', label: '人工转接', icon: '🔄' },
  { key: 'knowledge', label: '知识库', icon: '📚' },
  { key: 'script', label: '话术配置', icon: '💬' },
  { key: 'account', label: '账号权限', icon: '👤' }
]

function isActive(key) {
  return route.path === `/admin/${key}`
}

function navigateTo(key) {
  router.push(`/admin/${key}`)
}

function goBackToChat() {
  router.push('/chat')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  width: 100vw;
  height: 100vh;
  min-width: 1000px;
  overflow-x: auto;
  background: #f5f7fa;
}

.sidebar {
  width: 220px;
  min-width: 220px;
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.logo h3 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.menu {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: #f8f9fa;
}

.menu-item.active {
  background: #fff5e6;
  border-left-color: #ffb347;
  color: #ffb347;
}

.menu-item .icon {
  font-size: 18px;
}

.menu-item .text {
  font-size: 14px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #eee;
}

.btn-back {
  width: 100%;
  padding: 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #eee;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  padding: 0;
  width: 100%;
  min-width: 0;
}
</style>
