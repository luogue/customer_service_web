<template>
  <div class="admin-page">
    <h2>FAQ 管理</h2>
    
    <div class="toolbar">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="搜索问题或关键词..."
        />
      </div>
      <div class="toolbar-actions">
        <div class="upload-area" @click="triggerUpload" @drop.prevent="handleDrop" @dragover.prevent>
          <input 
            ref="fileInput" 
            type="file" 
            multiple 
            accept=".txt,.md"
            @change="handleFileSelect"
            style="display: none"
          />
          <span class="upload-icon">📄</span>
          <span>上传FAQ文件</span>
        </div>
        <button class="btn-primary" @click="showAddModal = true">
          + 新增FAQ
        </button>
      </div>
    </div>
    
    <div class="faq-list">
      <div 
        v-for="faq in filteredFAQs" 
        :key="faq.id"
        class="faq-item"
      >
        <div class="faq-header">
          <div class="faq-info">
            <span class="priority-badge" :class="'p' + faq.priority">
              P{{ faq.priority }}
            </span>
            <span class="match-type">{{ getMatchTypeText(faq.matchType) }}</span>
          </div>
          <div class="faq-actions">
            <button class="btn-edit" @click="editFAQ(faq)">编辑</button>
            <button class="btn-delete" @click="deleteFAQ(faq.id)">删除</button>
          </div>
        </div>
        <div class="faq-content">
          <div class="question">
            <strong>Q:</strong> {{ faq.question }}
          </div>
          <div class="keywords">
            <span v-for="keyword in faq.keywords" :key="keyword" class="keyword">
              {{ keyword }}
            </span>
          </div>
          <div class="answer">
            <strong>A:</strong> {{ faq.answer }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 新增/编辑弹窗 -->
    <div v-if="showAddModal || editingFAQ" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingFAQ ? '编辑FAQ' : '新增FAQ' }}</h3>
        
        <div class="form-group">
          <label>问题</label>
          <input v-model="form.question" type="text" placeholder="请输入问题" />
        </div>
        
        <div class="form-group">
          <label>关键词（用逗号分隔）</label>
          <input 
            v-model="keywordsInput" 
            type="text" 
            placeholder="例如：退货,退款,售后"
          />
        </div>
        
        <div class="form-group">
          <label>匹配方式</label>
          <select v-model="form.matchType">
            <option value="exact">精确匹配</option>
            <option value="contains">包含匹配</option>
            <option value="fuzzy">模糊匹配</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>优先级(1-5)</label>
          <input 
            v-model.number="form.priority" 
            type="range" 
            min="1" 
            max="5"
          />
          <span class="range-value">{{ form.priority }}</span>
        </div>
        
        <div class="form-group">
          <label>答案</label>
          <textarea 
            v-model="form.answer" 
            rows="5" 
            placeholder="请输入答案"
          ></textarea>
        </div>
        
        <div class="modal-actions">
          <button class="btn-primary" @click="saveFAQ">保存</button>
          <button class="btn-secondary" @click="closeModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const faqs = ref([
  {
    id: 1,
    question: '如何申请退款？',
    keywords: ['退货', '退款', '售后'],
    answer: '您可以在订单详情页点击申请退款按钮，填写退款原因后提交。我们会在1-3个工作日内处理。',
    matchType: 'contains',
    priority: 1
  },
  {
    id: 2,
    question: '订单什么时候发货？',
    keywords: ['发货', '物流', '快递'],
    answer: '一般情况下，订单会在付款后24小时内发货。您可以在订单详情页查看物流信息。',
    matchType: 'contains',
    priority: 2
  }
])

const searchQuery = ref('')
const showAddModal = ref(false)
const editingFAQ = ref(null)
const keywordsInput = ref('')
const fileInput = ref(null)

const form = reactive({
  question: '',
  keywords: [],
  answer: '',
  matchType: 'contains',
  priority: 3
})

const filteredFAQs = computed(() => {
  if (!searchQuery.value) return faqs.value
  const query = searchQuery.value.toLowerCase()
  return faqs.value.filter(faq => 
    faq.question.toLowerCase().includes(query) ||
    faq.keywords.some(k => k.toLowerCase().includes(query))
  )
})

function getMatchTypeText(type) {
  const map = {
    exact: '精确匹配',
    contains: '包含匹配',
    fuzzy: '模糊匹配'
  }
  return map[type] || type
}

function editFAQ(faq) {
  editingFAQ.value = faq
  form.question = faq.question
  form.answer = faq.answer
  form.matchType = faq.matchType
  form.priority = faq.priority
  keywordsInput.value = faq.keywords.join(',')
}

function closeModal() {
  showAddModal.value = false
  editingFAQ.value = null
  form.question = ''
  form.answer = ''
  form.matchType = 'contains'
  form.priority = 3
  keywordsInput.value = ''
}

function saveFAQ() {
  const keywords = keywordsInput.value.split(',').map(k => k.trim()).filter(k => k)
  
  if (editingFAQ.value) {
    editingFAQ.value.question = form.question
    editingFAQ.value.answer = form.answer
    editingFAQ.value.matchType = form.matchType
    editingFAQ.value.priority = form.priority
    editingFAQ.value.keywords = keywords
  } else {
    faqs.value.push({
      id: Date.now(),
      question: form.question,
      answer: form.answer,
      matchType: form.matchType,
      priority: form.priority,
      keywords
    })
  }
  closeModal()
}

function deleteFAQ(id) {
  if (confirm('确定要删除这个FAQ吗？')) {
    faqs.value = faqs.value.filter(f => f.id !== id)
  }
}

// 文件上传相关函数
function triggerUpload() {
  fileInput.value.click()
}

async function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    try {
      await processFile(file)
    } catch (error) {
      console.error('文件处理失败:', error)
      window.showMessage('文件处理失败: ' + error.message, 'error')
    }
  }
}

async function handleDrop(e) {
  const files = Array.from(e.dataTransfer.files)
  for (const file of files) {
    try {
      await processFile(file)
    } catch (error) {
      console.error('文件处理失败:', error)
      window.showMessage('文件处理失败: ' + error.message, 'error')
    }
  }
}

async function processFile(file) {
  // 读取文件内容
  const content = await readFileContent(file)
  
  // 处理FAQ文件
  await processFAQFile(content)
}

function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(new Error('文件读取失败'))
    reader.readAsText(file, 'utf-8')
  })
}

async function processFAQFile(content) {
  // 按 "问题 || 答案" 格式拆分内容
  const faqPairs = content.split('\n').filter(line => line.trim() && line.includes('||'))
  
  if (faqPairs.length === 0) {
    throw new Error('文件中没有找到符合格式的FAQ内容')
  }
  
  for (const pair of faqPairs) {
    const [question, answer] = pair.split('||').map(item => item.trim())
    if (question && answer) {
      // 发送到后端API
      await saveFAQFromFile(question, answer)
      
      // 添加到本地列表
      faqs.value.push({
        id: Date.now() + Math.random(),
        question: question,
        answer: answer,
        keywords: question.split(' ').filter(k => k),
        matchType: 'contains',
        priority: 3
      })
    }
  }
}

async function saveFAQFromFile(question, answer) {
  try {
    const response = await fetch('http://localhost:8004/api/knowledge/faqs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question: question,
        answer: answer,
        keywords: question.split(' ').join(',')
      })
    })
    
    if (!response.ok) {
      throw new Error('保存FAQ失败')
    }
  } catch (error) {
    console.error('保存FAQ失败:', error)
    throw error
  }
}
</script>

<style scoped>
.admin-page {
  padding: 24px;
}

.admin-page h2 {
  margin-bottom: 24px;
  color: #333;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-box input {
  width: 300px;
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.upload-area {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #ffb347;
  background: #f0f2ff;
}

.upload-icon {
  font-size: 16px;
}

.upload-area span {
  font-size: 14px;
  color: #333;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.faq-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.faq-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.faq-info {
  display: flex;
  gap: 10px;
  align-items: center;
}

.priority-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.priority-badge.p1 { background: #ffebee; color: #c62828; }
.priority-badge.p2 { background: #fff3e0; color: #ef6c00; }
.priority-badge.p3 { background: #fffde7; color: #f9a825; }
.priority-badge.p4 { background: #e8f5e9; color: #2e7d32; }
.priority-badge.p5 { background: #e3f2fd; color: #1565c0; }

.match-type {
  font-size: 12px;
  color: #999;
  background: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.faq-actions {
  display: flex;
  gap: 8px;
}

.faq-actions button {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: none;
}

.btn-edit {
  background: #ffb347;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.faq-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question {
  font-size: 15px;
  color: #333;
}

.keywords {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.keyword {
  background: #f0f0f0;
  color: #666;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.answer {
  font-size: 14px;
  color: #666;
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 24px;
  width: 500px;
  max-width: 90%;
}

.modal h3 {
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.form-group select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  width: auto;
  min-width: 200px;
}

.range-value {
  margin-left: 12px;
  color: #ffb347;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-secondary {
  padding: 10px 20px;
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
</style>
