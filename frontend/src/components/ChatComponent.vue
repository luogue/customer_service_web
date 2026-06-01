<template>
  <div class="chat-container">
    <div class="chat-header">
      <div class="header-info">
        <div class="avatar">
          <span>客服</span>
        </div>
        <div class="header-text">
          <h3>在线客服</h3>
          <p class="status" :class="{ 'human-service': isHumanService }">
            {{ isHumanService ? '人工服务中' : '在线' }}
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="history-btn" @click="toggleHistory">历史会话</button>
        <button class="history-btn" @click="clearMessages">清除记录</button>
      </div>
    </div>

    <!-- 历史会话列表 -->
    <div class="chat-history" v-if="showHistory">
      <h3>历史会话</h3>
      <div class="history-list">
        <div v-for="session in sessionHistory" :key="session.session_id" class="history-item" @click="loadSession(session)">
          <div class="history-time">{{ formatTime(session.created_at) }}</div>
          <div class="history-preview">{{ session.preview || '无消息' }}</div>
        </div>
        <div v-if="sessionHistory.length === 0" class="no-history">暂无历史会话</div>
      </div>
      <button class="close-history-btn" @click="showHistory = false">关闭</button>
    </div>
    
    <!-- 聊天消息区域 -->
    <div class="chat-messages" ref="messagesContainer" v-if="!showHistory" :class="{ 'hide-scrollbar': isRestoringScroll }">
      <div
        v-for="message in messages"
        :key="message.id"
        :class="['message', message.type, { streaming: message.isStreaming }]"
      >
        <div class="message-avatar">
          {{ message.type === 'user' ? '用户' : '客服' }}
        </div>
        <div class="message-content">
          <div class="message-bubble">
            {{ message.text }}
            <span v-if="message.isStreaming" class="streaming-indicator">●</span>
          </div>
          <div class="message-time">{{ message.time }}</div>
        </div>
      </div>
    </div>

    <!-- 输入区域 -->
    <div class="chat-input" v-if="!showHistory">
      <textarea
        v-model="inputText"
        placeholder="请输入消息.."
        @keydown.enter.prevent="sendMessage"
        @input="autoResize"
        ref="textarea"
      ></textarea>
      <div class="input-buttons">
        <button 
          v-if="isHumanService" 
          class="human-end-btn" 
          @click="endHumanService"
          :disabled="isStreaming"
        >
          人工结束会话
        </button>
        <button class="send-btn" @click="sendMessage" :disabled="!inputText.trim() || isStreaming">
          发送      </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'

const API_BASE_URL = 'http://localhost:8004/api'
const STORAGE_KEY_MESSAGES = 'customer_service_messages'
const STORAGE_KEY_SESSION = 'customer_service_session'
const STORAGE_KEY_BUSINESS_CONTEXT = 'customer_service_business_context'
const STORAGE_KEY_HUMAN_SERVICE = 'customer_service_human_service'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  userRole: {
    type: String,
    default: 'user'
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'sendMessage'])

const messages = ref([])
const inputText = ref('')
const messagesContainer = ref(null)
const textarea = ref(null)
const isStreaming = ref(false)
const currentStreamingMessage = ref(null)
const isHumanService = ref(false)
const showHistory = ref(false)
const isRestoringScroll = ref(false)
const sessionHistory = ref([])
let humanServiceTimer = null

// 从localStorage获取或生成session_id
const sessionId = ref('')
const userId = ref('')

// 生成随机字符串
function generateRandomString(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

// 初始化userId和sessionId
async function initUserAndSessionId() {
  // 初始化userId
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    try {
      const userData = JSON.parse(savedUser)
      userId.value = userData.id || userData.phone || 'default_user'
    } catch (e) {
      console.error('解析用户信息失败:', e)
      userId.value = 'default_user'
    }
  } else {
    userId.value = 'default_user'
  }
  
  // 检查本地是否缓存有未过期的sessionId
  const savedSession = localStorage.getItem(STORAGE_KEY_SESSION)
  if (savedSession) {
    try {
      const sessionData = JSON.parse(savedSession)
      const cachedSessionId = sessionData.sessionId
      
      // 验证会话是否过期
      const isValid = await validateSession(cachedSessionId)
      if (isValid) {
        // 会话有效，复用sessionId
        sessionId.value = cachedSessionId
        console.log('复用会话:', sessionId.value)
        saveSessionToStorage()
        return
      } else {
        // 会话过期，清除本地缓存
        localStorage.removeItem(STORAGE_KEY_SESSION)
        console.log('会话已过期，清除缓存')
      }
    } catch (e) {
      console.error('解析会话信息失败:', e)
    }
  }
  
  // 生成新的sessionId
  sessionId.value = 'session_' + Date.now() + '_' + generateRandomString()
  saveSessionToStorage()
  console.log('生成新会话:', sessionId.value)
}

// 验证会话是否有效
async function validateSession(cachedSessionId) {
  try {
    const response = await fetchWithAuth(`${API_BASE_URL}/chat/validate-session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId.value,
        session_id: cachedSessionId
      })
    })
    
    const data = await response.json()
    return data.success
  } catch (e) {
    console.error('验证会话失败:', e)
    return false
  }
}

// 带认证的fetch请求
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    ...options.headers,
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return fetch(url, {
    ...options,
    headers
  })
}

// 初始化时从localStorage加载数据
async function loadFromStorage() {
  await initUserAndSessionId()
  try {
    const savedMessages = localStorage.getItem(STORAGE_KEY_MESSAGES)
    if (savedMessages) {
      messages.value = JSON.parse(savedMessages)
    }
    
    const savedHumanService = localStorage.getItem(STORAGE_KEY_HUMAN_SERVICE)
    if (savedHumanService) {
      try {
        const humanServiceData = JSON.parse(savedHumanService)
        isHumanService.value = humanServiceData.isHumanService
        if (isHumanService.value) {
          startHumanServiceTimer()
        }
      } catch (e) {
        console.error('解析人工服务状态失败:', e)
      }
    }
  } catch (e) {
    console.error('从localStorage加载数据失败:', e)
  }
}

// 保存消息到localStorage
function saveMessagesToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY_MESSAGES, JSON.stringify(messages.value))
  } catch (e) {
    console.error('保存消息到localStorage失败:', e)
  }
}

// 保存会话信息到localStorage
function saveSessionToStorage() {
  try {
    // 保存当前会话信息
    localStorage.setItem(STORAGE_KEY_SESSION, JSON.stringify({
      sessionId: sessionId.value,
      createdAt: new Date().toISOString()
    }))
    
    // 更新历史会话列表
    updateSessionHistory()
  } catch (e) {
    console.error('保存会话信息到localStorage失败:', e)
  }
}

// 更新历史会话列表
function updateSessionHistory() {
  try {
    // 从localStorage加载历史会话
    let history = []
    const sessionHistoryData = localStorage.getItem('customer_service_session_history')
    if (sessionHistoryData) {
      history = JSON.parse(sessionHistoryData)
    }
    
    // 查找当前会话是否已存在
    const sessionIndex = history.findIndex(s => s.session_id === sessionId.value)
    
    // 获取最后一条消息作为预览
    let preview = ''
    if (messages.value.length > 0) {
      const lastMessage = messages.value[messages.value.length - 1]
      preview = lastMessage.text.substring(0, 50) + (lastMessage.text.length > 50 ? '...' : '')
    }
    
    const sessionData = {
      session_id: sessionId.value,
      created_at: new Date().toISOString(),
      preview: preview,
      messages: messages.value
    }
    
    if (sessionIndex >= 0) {
      // 更新现有会话
      history[sessionIndex] = sessionData
    } else {
      // 添加新会话
      history.unshift(sessionData)
      // 只保留最近10个会话
      if (history.length > 10) {
        history = history.slice(0, 10)
      }
    }
    
    // 保存到localStorage
    localStorage.setItem('customer_service_session_history', JSON.stringify(history))
  } catch (e) {
    console.error('更新历史会话列表失败:', e)
  }
}

// 保存人工服务状态到localStorage
function saveHumanServiceToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY_HUMAN_SERVICE, JSON.stringify({
      isHumanService: isHumanService.value,
      updatedAt: new Date().toISOString()
    }))
  } catch (e) {
    console.error('保存人工服务状态到localStorage失败:', e)
  }
}

// 保存业务上下文到localStorage
function saveBusinessContextToStorage(context) {
  try {
    localStorage.setItem(STORAGE_KEY_BUSINESS_CONTEXT, JSON.stringify({
      ...context,
      updatedAt: new Date().toISOString()
    }))
  } catch (e) {
    console.error('保存业务上下文到localStorage失败:', e)
  }
}

// 从localStorage获取业务上下文
function loadBusinessContextFromStorage() {
  try {
    const savedContext = localStorage.getItem(STORAGE_KEY_BUSINESS_CONTEXT)
    if (savedContext) {
      return JSON.parse(savedContext)
    }
  } catch (e) {
    console.error('从localStorage加载业务上下文失败:', e)
  }
  return null
}

// 获取当前登录用户的手机号
function getCurrentUserPhone() {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      return user.phone || '13800000000'
    } catch (e) {
      console.error('解析用户信息失败:', e)
      return '13800000000'
    }
  }
  return '13800000000'
}

function getCurrentTime() {
  const now = new Date()
  return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
}

// 切换历史会话显示/隐藏
function toggleHistory() {
  showHistory.value = !showHistory.value
  if (showHistory.value) {
    loadSessionHistory()
  }
}

// 加载历史会话列表
async function loadSessionHistory() {
  try {
    // 从localStorage加载历史会话
    const sessionHistoryData = localStorage.getItem('customer_service_session_history')
    if (sessionHistoryData) {
      sessionHistory.value = JSON.parse(sessionHistoryData)
    } else {
      sessionHistory.value = []
    }
  } catch (e) {
    console.error('加载历史会话失败:', e)
    sessionHistory.value = []
  }
}

// 加载历史会话
function loadSession(session) {
  sessionId.value = session.session_id
  messages.value = []
  saveSessionToStorage()
  showHistory.value = false
  setTimeout(() => {
    isRestoringScroll.value = true
    messages.value = session.messages || []
    saveMessagesToStorage()
  }, 50)
}

// 格式化时间
function formatTime(timeString) {
  const date = new Date(timeString)
  return date.toLocaleString()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      const container = messagesContainer.value
      const targetScroll = container.scrollHeight
      container.scrollTop = targetScroll
      if (isRestoringScroll.value) {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            isRestoringScroll.value = false
          })
        })
      }
    }
  })
}

function isAtBottom() {
  if (!messagesContainer.value) return false
  const container = messagesContainer.value
  const threshold = 10
  const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight
  return distanceToBottom < threshold
}

function scrollToBottomIfNeeded() {
  if (isAtBottom()) {
    scrollToBottom()
  }
}

function autoResize() {
  if (textarea.value) {
    textarea.value.style.height = 'auto'
    textarea.value.style.height = Math.min(textarea.value.scrollHeight, 120) + 'px'
  }
}

function fetchWelcomeMessage() {
  // 只在消息列表为空时添加首问语
  if (messages.value.length === 0) {
    messages.value.push({
      id: 1,
      text: '您好，这里是AI客服，很高兴为您服务，请问有什么可以帮您？',
      type: 'ai',
      time: getCurrentTime()
    })
    saveMessagesToStorage()
  }
}

// 开始人工服务定时器
function startHumanServiceTimer() {
  // 清除之前的定时器
  if (humanServiceTimer) {
    clearTimeout(humanServiceTimer)
  }
  
  // 设置5分钟超时
  humanServiceTimer = setTimeout(() => {
    endHumanService(true)
  }, 5 * 60 * 1000)
}

// 重置人工服务定时器
function resetHumanServiceTimer() {
  if (isHumanService.value) {
    startHumanServiceTimer()
  }
}

// 结束人工服务
function endHumanService(isTimeout = false) {
  isHumanService.value = false
  saveHumanServiceToStorage()
  
  // 清除定时器
  if (humanServiceTimer) {
    clearTimeout(humanServiceTimer)
    humanServiceTimer = null
  }
  
  // 添加系统消息
  const endMessage = {
    id: messages.value.length + 1,
    text: isTimeout ? '人工服务超时，已自动恢复AI服务' : '人工服务已结束，已恢复AI服务',
    type: 'system',
    time: getCurrentTime()
  }
  messages.value.push(endMessage)
  saveMessagesToStorage()
  scrollToBottomIfNeeded()
  
  // 向后端发送重置会话状态的消息
  const resetMessage = '重置会话状态'
  sendWithSSE(resetMessage)
}

// 会话过期提示定时器
let sessionExpiryTimer = null

// 开始会话过期提示
function startSessionExpiryTimer() {
  // 清除之前的定时器
  if (sessionExpiryTimer) {
    clearTimeout(sessionExpiryTimer)
  }
  
  // 9分钟后提示会话即将过期（10分钟有效期）
  sessionExpiryTimer = setTimeout(() => {
    // 添加系统消息提示
    const expiryMessage = {
      id: messages.value.length + 1,
      text: '会话即将结束，如需继续聊请发送一条消息',
      type: 'system',
      time: getCurrentTime()
    }
    messages.value.push(expiryMessage)
    saveMessagesToStorage()
    scrollToBottomIfNeeded()
  }, 9 * 60 * 1000) // 9分钟
}

// 重置会话过期提示
function resetSessionExpiryTimer() {
  startSessionExpiryTimer()
}

// 清除聊天记录
function clearMessages() {
  messages.value = []
  localStorage.removeItem(STORAGE_KEY_MESSAGES)
  // 清除历史会话记录
  localStorage.removeItem('customer_service_session_history')
  sessionHistory.value = []
  // 生成新的sessionId
  sessionId.value = 'session_' + Date.now() + '_' + generateRandomString()
  saveSessionToStorage()
  scrollToBottom()
}

function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isStreaming.value) return

  sendWithSSE(text)
  // 重置人工服务定时器
  resetHumanServiceTimer()
  // 重置会话过期提示定时器
  resetSessionExpiryTimer()
}

async function sendWithSSE(text) {
  console.log('sendWithSSE 开始，当前 isStreaming:', isStreaming.value)
  try {
    console.log('开始发送SSE:', text)
    isStreaming.value = true
    console.log('设置 isStreaming = true')
    
    const userMessage = {
      id: messages.value.length + 1,
      text: text,
      type: 'user',
      time: getCurrentTime()
    }
    messages.value.push(userMessage)
    saveMessagesToStorage()
    emit('sendMessage', text)
    inputText.value = ''
    autoResize()
    scrollToBottomIfNeeded()
    
    currentStreamingMessage.value = {
      id: messages.value.length + 2,
      text: '',
      type: 'ai',
      time: getCurrentTime(),
      isStreaming: true
    }
    messages.value.push(currentStreamingMessage.value)
    saveMessagesToStorage()
    scrollToBottomIfNeeded()
    
    console.log('发送请求到:', `${API_BASE_URL}/chat/message`)
    const response = await fetchWithAuth(`${API_BASE_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: text,
        user_id: userId.value,
        session_id: sessionId.value,
        phone: getCurrentUserPhone()
      })
    })
    
    console.log('响应状态:', response.status, response.ok)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    console.log('开始读取流')
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    
    while (true) {
      const { done, value } = await reader.read()
      console.log('读取数据:', done, value)
      if (done) {
        console.log('流读取完成')
        break
      }
      
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') {
                console.log('收到结束标记')
                currentStreamingMessage.value.isStreaming = false
                saveMessagesToStorage()
                isStreaming.value = false
                
                // 更新历史会话列表
                updateSessionHistory()
                
                // 检查是否进入了人工服务状态
                if (currentStreamingMessage.value.text.includes('转接人工客服')) {
                    isHumanService.value = true
                    saveHumanServiceToStorage()
                    startHumanServiceTimer()
                }
            } else {
            try {
              const json = JSON.parse(data)
              if (json.content) {
                console.log('收到片段:', json.content)
                currentStreamingMessage.value.text += json.content
                saveMessagesToStorage()
                scrollToBottomIfNeeded()
              }
            } catch (e) {
              console.log('解析错误:', e)
            }
          }
        }
      }
    }
  } catch (error) {
    console.error('SSE发送消息失败', error)
    isStreaming.value = false
    if (currentStreamingMessage.value) {
      currentStreamingMessage.value.isStreaming = false
    }
  } finally {
    console.log('SSE请求完成，重置状态，当前 isStreaming:', isStreaming.value)
    isStreaming.value = false
    if (currentStreamingMessage.value) {
      currentStreamingMessage.value.isStreaming = false
    }
    saveMessagesToStorage()
    console.log('重置后 isStreaming:', isStreaming.value)
  }
}

onMounted(async () => {
  await loadFromStorage()
  saveSessionToStorage()
  fetchWelcomeMessage()
  // 开始会话过期提示定时器
  startSessionExpiryTimer()
})

onUnmounted(() => {
  // 清理定时器
  if (humanServiceTimer) {
    clearTimeout(humanServiceTimer)
  }
  // 清理会话过期提示定时器
  if (sessionExpiryTimer) {
    clearTimeout(sessionExpiryTimer)
  }
})

watch(messages, () => {
  scrollToBottomIfNeeded()
}, { deep: true })

watch(showHistory, (newVal, oldVal) => {
  if (oldVal === true && newVal === false) {
    isRestoringScroll.value = true
    setTimeout(() => {
      nextTick(() => {
        nextTick(() => {
          scrollToBottom()
        })
      })
    }, 300)
  }
})
</script>

<style scoped>
.chat-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f0f2f5;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.history-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
}

.header-text h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 2px;
}

.status {
  font-size: 12px;
  opacity: 0.9;
}

.status.human-service {
  color: #e74c3c;
  font-weight: 500;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    opacity: 0.9;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.9;
  }
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f5f5f5;
}

.chat-messages.hide-scrollbar {
  overflow-y: hidden;
}

/* 历史会话列表样式 */
.chat-history {
  flex: 1;
  padding: 20px;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-history h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
  flex-shrink: 0;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 280px);
}

.history-item {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.history-time {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.history-preview {
  font-size: 14px;
  color: #333;
  line-height: 1.4;
}

.no-history {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}

.close-history-btn {
  margin-top: 16px;
  padding: 8px 16px;
  background: #ffb347;
  color: #333;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: center;
}

.close-history-btn:hover {
  background: #ffd793;
  transform: translateY(-1px);
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  color: #333;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: linear-gradient(135deg, #ffd793 0%, #ffb347 100%);
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
}

.message.user .message-content {
  align-items: flex-end;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  min-height: 20px;
  display: inline-block;
  white-space: pre-wrap;
}

.message.system .message-bubble {
  background: white;
  border-bottom-left-radius: 4px;
  color: #e74c3c;
  font-weight: 500;
}

.message.user .message-bubble {
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  color: #333;
  border-bottom-right-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 4px;
}

.chat-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-input textarea {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  padding: 12px 16px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  min-height: 44px;
  max-height: 120px;
  transition: border-color 0.2s;
}

.chat-input textarea:focus {
  border-color: #ffb347;
}

.input-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.human-end-btn {
  padding: 10px 16px;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.human-end-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
}

.human-end-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #ffb347 0%, #ffd793 100%);
  color: #333;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

.message.streaming {
  opacity: 0.8;
}

.message.streaming .message-bubble {
  border: 2px solid #ffb347;
}

.streaming-indicator {
  margin-left: 8px;
  animation: blink 1s infinite;
  color: #ffb347;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}
</style>
