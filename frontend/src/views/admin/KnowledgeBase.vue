<template>
  <div class="admin-page">
    <h2>知识库管理</h2>
    
    <!-- 上传区域移到最上面 -->
    <div class="upload-section">
      <div class="upload-area" @click="triggerUpload" @drop.prevent="handleDrop" @dragover.prevent>
        <input 
          ref="fileInput" 
          type="file" 
          multiple 
          accept=".pdf,.doc,.docx,.txt,.md"
          @change="handleFileSelect"
          style="display: none"
        />
        <div class="upload-icon">📄</div>
        <p>点击或拖拽上传文件到知识库</p>
        <span>支持 PDF、Word、TXT、Markdown（自动创建新文档）</span>
      </div>
    </div>
    
    <div class="toolbar">
      <button class="btn-add" @click="showAddDocDialog = true">新建文档</button>
    </div>
    
    <div class="settings-section">
      <div class="setting-card">
        <h3>检索配置</h3>
        <div class="form-group">
          <label>相似度阈值 (0-1)</label>
          <input 
            v-model.number="settings.similarityThreshold" 
            type="number" 
            min="0" 
            max="1" 
            step="0.1"
          />
        </div>
        <div class="form-group">
          <label>最大检索结果数</label>
          <input v-model.number="settings.maxResults" type="number" min="1" max="20" />
        </div>
        <div class="form-group">
          <label>检索模式</label>
          <select v-model="settings.searchMode">
            <option value="hybrid">混合检索</option>
            <option value="text">文本检索</option>
            <option value="vector">向量检索</option>
          </select>
        </div>
        <button class="btn-save" @click="saveSettings">保存配置</button>
      </div>
    </div>
    
    <div class="main-content">
      <div class="documents-panel">
        <h3>文档列表</h3>
        <div class="document-list">
          <div 
            v-for="doc in documents" 
            :key="doc.id"
            class="document-item"
            :class="{ active: selectedDocument && selectedDocument.id === doc.id }"
            @click="selectDocument(doc)"
          >
            <div class="document-title">{{ doc.title }}</div>
            <div class="document-meta">
              <span>{{ formatDate(doc.create_time) }}</span>
              <button class="btn-delete-small" @click.stop="deleteDoc(doc.id)">×</button>
            </div>
          </div>
          
          <div v-if="loading" class="loading">加载中...</div>
          <div v-if="documents.length === 0 && !loading" class="empty">
            暂无文档，点击"新建文档"创建
          </div>
        </div>
      </div>
      
      <div class="knowledge-panel" v-if="selectedDocument">
        <div class="panel-header">
          <h3>{{ selectedDocument.title }} - 内容</h3>
          <button class="btn-add-small" @click="showAddKnowledgeDialog = true">
            新增内容
          </button>
        </div>
        
        <div class="knowledge-list">
          <div v-for="knowledge in paginatedKnowledgeList" :key="knowledge.id" class="knowledge-item">
            <div class="knowledge-content">{{ knowledge.content }}</div>
            <div class="knowledge-meta">
              <span>{{ formatDate(knowledge.created_at) }}</span>
              <button class="btn-delete-small" @click="deleteKnowledge(knowledge.id)">×</button>
            </div>
          </div>
          
          <div v-if="loadingKnowledge" class="loading">加载中...</div>
          <div v-if="knowledgeList.length === 0 && !loadingKnowledge" class="empty">
            暂无内容，点击"新增内容"添加
          </div>
        </div>
        
        <!-- 分页控件 -->
        <div v-if="totalPages > 1" class="pagination">
          <button 
            class="btn-page" 
            :disabled="currentPage === 1"
            @click="currentPage--"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
          <button 
            class="btn-page" 
            :disabled="currentPage === totalPages"
            @click="currentPage++"
          >
            下一页
          </button>
        </div>
      </div>
      
      <div v-else class="empty-panel">
        <div class="empty-state">
          <div class="empty-icon">📁</div>
          <h4>请选择一个文档</h4>
          <p>从左侧选择一个文档或创建新文档</p>
        </div>
      </div>
    </div>
    
    <!-- 新建文档弹窗 -->
    <div v-if="showAddDocDialog" class="dialog-overlay" @click="showAddDocDialog = false">
      <div class="dialog" @click.stop>
        <h3>新建文档</h3>
        <div class="form-group">
          <label>文档标题</label>
          <input v-model="newDoc.title" type="text" placeholder="请输入文档标题" />
        </div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showAddDocDialog = false">取消</button>
          <button class="btn-confirm" @click="addDocument">确定</button>
        </div>
      </div>
    </div>
    
    <!-- 新增内容弹窗 -->
    <div v-if="showAddKnowledgeDialog" class="dialog-overlay" @click="showAddKnowledgeDialog = false">
      <div class="dialog" @click.stop>
        <h3>新增内容</h3>
        <div class="form-group">
          <label>归属文档</label>
          <select v-model="newKnowledge.document_id" disabled>
            <option :value="selectedDocument.id">{{ selectedDocument.title }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>内容</label>
          <textarea v-model="newKnowledge.content" placeholder="请输入内容" rows="10"></textarea>
        </div>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showAddKnowledgeDialog = false">取消</button>
          <button class="btn-confirm" @click="addKnowledge">确定</button>
        </div>
      </div>
    </div>
    
    <!-- 确认删除弹窗 -->
    <div v-if="showConfirmDialog" class="dialog-overlay" @click="showConfirmDialog = false">
      <div class="dialog" @click.stop>
        <h3>{{ confirmTitle }}</h3>
        <p style="margin: 20px 0; color: #666;">{{ confirmMessage }}</p>
        <div class="dialog-actions">
          <button class="btn-cancel" @click="showConfirmDialog = false">取消</button>
          <button class="btn-confirm" @click="executeConfirm">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'

const fileInput = ref(null)
const loading = ref(false)
const loadingKnowledge = ref(false)
const error = ref('')
const showAddDocDialog = ref(false)
const showAddKnowledgeDialog = ref(false)
const showConfirmDialog = ref(false)

const documents = ref([])
const knowledgeList = ref([])
const selectedDocument = ref(null)
const newCategoryName = ref('')

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)

// 确认对话框相关
const confirmTitle = ref('')
const confirmMessage = ref('')
let confirmCallback = null

const settings = reactive({
  similarityThreshold: 0.7,
  maxResults: 10,
  searchMode: 'hybrid'
})

const newDoc = reactive({
  title: ''
})

const newKnowledge = reactive({
  content: '',
  document_id: null
})

// 计算分页后的内容列表
const paginatedKnowledgeList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return knowledgeList.value.slice(start, end)
})

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(knowledgeList.value.length / pageSize.value)
})

onMounted(() => {
  loadDocuments()
  loadSettings()
})

async function loadDocuments() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://localhost:8004/api/knowledge/documents?limit=100')
    if (!response.ok) {
      throw new Error('加载文档列表失败')
    }
    const data = await response.json()
    documents.value = data.documents || []
  } catch (err) {
    console.error('加载文档列表失败:', err)
    error.value = '加载文档列表失败: ' + err.message
  } finally {
    loading.value = false
  }
}

async function loadKnowledgeList(documentId) {
  loadingKnowledge.value = true
  
  try {
    const response = await fetch(`http://localhost:8004/api/knowledge/knowledge/document/${documentId}`)
    if (!response.ok) {
      throw new Error('加载内容失败')
    }
    const data = await response.json()
    knowledgeList.value = data.knowledge_list || []
  } catch (err) {
    console.error('加载内容失败:', err)
    window.showMessage('加载内容失败: ' + err.message, 'error')
  } finally {
    loadingKnowledge.value = false
  }
}

async function loadSettings() {
  try {
    const response = await fetch('http://localhost:8004/api/knowledge/configs')
    if (!response.ok) {
      throw new Error('加载配置失败')
    }
    const data = await response.json()
    const configs = data.configs || []
    
    configs.forEach(config => {
      if (config.config_key === 'similarity_threshold') {
        settings.similarityThreshold = parseFloat(config.config_value)
      } else if (config.config_key === 'max_results') {
        settings.maxResults = parseInt(config.config_value)
      } else if (config.config_key === 'search_mode') {
        settings.searchMode = config.config_value
      }
    })
  } catch (err) {
    console.error('加载配置失败:', err)
  }
}

async function saveSettings() {
  try {
    const configs = [
      { config_key: 'similarity_threshold', config_value: settings.similarityThreshold.toString() },
      { config_key: 'max_results', config_value: settings.maxResults.toString() },
      { config_key: 'search_mode', config_value: settings.searchMode }
    ]
    
    for (const config of configs) {
      const response = await fetch('http://localhost:8004/api/knowledge/configs', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      })
      
      if (!response.ok) {
        throw new Error('保存配置失败')
      }
    }
    
    window.showMessage('配置已保存', 'success')
  } catch (err) {
    console.error('保存配置失败:', err)
    window.showMessage('保存配置失败: ' + err.message, 'error')
  }
}

function selectDocument(doc) {
  selectedDocument.value = doc
  newKnowledge.document_id = doc.id
  currentPage.value = 1  // 重置页码
  loadKnowledgeList(doc.id)
}

function triggerUpload() {
  fileInput.value.click()
}

async function handleFileSelect(e) {
  const files = Array.from(e.target.files)
  for (const file of files) {
    await processFile(file)
  }
  fileInput.value.value = ''
}

async function handleDrop(e) {
  const files = Array.from(e.dataTransfer.files)
  for (const file of files) {
    await processFile(file)
  }
}

async function processFile(file) {
  try {
    // 文件大小校验（100MB）
    const maxFileSizeMB = 100
    const maxFileSizeBytes = maxFileSizeMB * 1024 * 1024
    
    if (file.size > maxFileSizeBytes) {
      window.showMessage(`文件大小超过限制（最大 ${maxFileSizeMB}MB）`, 'error')
      return
    }
    
    const content = await readFileContent(file)
    
    // 文本块大小校验（1000字）
    const maxTextChunkSize = 1000
    if (content.length > maxTextChunkSize) {
      window.showMessage(`文件内容超过单文本块限制（最大 ${maxTextChunkSize}字），将自动分块处理`, 'warning')
    }
    
    // 创建新文档
    const docResponse = await fetch('http://localhost:8004/api/knowledge/documents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: file.name.replace(/\.[^/.]+$/, '') // 去掉扩展名
      })
    })
    
    if (!docResponse.ok) {
      throw new Error('创建文档失败')
    }
    
    const docData = await docResponse.json()
    const documentId = docData.document.id
    
    // 按换行符分割内容为多个碎片
    const chunks = content.split(/\n\s*\n/).filter(chunk => chunk.trim())
    
    for (const chunk of chunks) {
      // 确保每个分块不超过限制
      if (chunk.length > maxTextChunkSize) {
        // 进一步拆分大块文本
        const subChunks = []
        let currentChunk = ''
        
        for (const sentence of chunk.split(/[。！？；]/)) {
          if (currentChunk.length + sentence.length + 1 <= maxTextChunkSize) {
            currentChunk += sentence + '。'
          } else {
            if (currentChunk) {
              subChunks.push(currentChunk)
            }
            currentChunk = sentence + '。'
          }
        }
        
        if (currentChunk) {
          subChunks.push(currentChunk)
        }
        
        // 上传子分块
        for (const subChunk of subChunks) {
          await fetch('http://localhost:8004/api/knowledge/knowledge', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              content: subChunk,
              document_id: documentId
            })
          })
        }
      } else {
        // 直接上传分块
        await fetch('http://localhost:8004/api/knowledge/knowledge', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            content: chunk,
            document_id: documentId
          })
        })
      }
    }
    
    await loadDocuments()
    window.showMessage(`文档 "${file.name}" 上传成功`, 'success')
  } catch (err) {
    console.error('上传文件失败:', err)
    window.showMessage('上传文件失败: ' + err.message, 'error')
  }
}

function readFileContent(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(new Error('文件读取失败'))
    reader.readAsText(file, 'utf-8')
  })
}

async function addDocument() {
  if (!newDoc.title.trim()) {
    window.showMessage('请填写文档标题', 'warning')
    return
  }
  
  try {
    const response = await fetch('http://localhost:8004/api/knowledge/documents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: newDoc.title.trim()
      })
    })
    
    if (!response.ok) {
      throw new Error('新增文档失败')
    }
    
    showAddDocDialog.value = false
    window.showMessage('文档创建成功', 'success')
    newDoc.title = ''
    
    await loadDocuments()
  } catch (err) {
    console.error('新增文档失败:', err)
    window.showMessage('新增文档失败: ' + err.message, 'error')
  }
}

async function addKnowledge() {
  if (!newKnowledge.content.trim()) {
    window.showMessage('请填写内容', 'warning')
    return
  }
  
  try {
    const response = await fetch('http://localhost:8004/api/knowledge/knowledge', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        content: newKnowledge.content.trim(),
        document_id: newKnowledge.document_id
      })
    })
    
    if (!response.ok) {
      throw new Error('新增内容失败')
    }
    
    showAddKnowledgeDialog.value = false
    window.showMessage('内容添加成功', 'success')
    newKnowledge.content = ''
    
    await loadKnowledgeList(selectedDocument.value.id)
  } catch (err) {
    console.error('新增内容失败:', err)
    window.showMessage('新增内容失败: ' + err.message, 'error')
  }
}

function deleteDoc(id) {
  confirmTitle.value = '确认删除'
  confirmMessage.value = '确定要删除这个文档吗？删除后文档下的所有内容也将被删除。'
  confirmCallback = async () => {
    try {
      const response = await fetch(`http://localhost:8004/api/knowledge/documents/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('删除文档失败')
      }
      
      showConfirmDialog.value = false
      window.showMessage('文档删除成功', 'success')
      await loadDocuments()
      if (selectedDocument.value && selectedDocument.value.id === id) {
        selectedDocument.value = null
        knowledgeList.value = []
      }
    } catch (err) {
      console.error('删除文档失败:', err)
      showConfirmDialog.value = false
      window.showMessage('删除文档失败: ' + err.message, 'error')
    }
  }
  showConfirmDialog.value = true
}

function deleteKnowledge(id) {
  confirmTitle.value = '确认删除'
  confirmMessage.value = '确定要删除这个内容吗？删除后无法恢复。'
  confirmCallback = async () => {
    try {
      const response = await fetch(`http://localhost:8004/api/knowledge/knowledge/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('删除内容失败')
      }
      
      showConfirmDialog.value = false
      window.showMessage('内容删除成功', 'success')
      await loadKnowledgeList(selectedDocument.value.id)
    } catch (err) {
      console.error('删除内容失败:', err)
      showConfirmDialog.value = false
      window.showMessage('删除内容失败: ' + err.message, 'error')
    }
  }
  showConfirmDialog.value = true
}

function executeConfirm() {
  if (confirmCallback) {
    confirmCallback()
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
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

.upload-section {
  margin-bottom: 24px;
}

.upload-area {
  background: #f8f9fa;
  border: 2px dashed #ddd;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  border-color: #ffb347;
  background: #f0f2ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.upload-area p {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.upload-area span {
  font-size: 13px;
  color: #999;
}

.toolbar {
  margin-bottom: 24px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-add {
  padding: 12px 24px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.btn-add:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.settings-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.setting-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.setting-card h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}

.form-group select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
  width: auto;
  min-width: 200px;
}

.btn-save {
  padding: 10px 20px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  width: auto;
  display: inline-block;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.main-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.documents-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.documents-panel h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
}

.document-list {
  max-height: 600px;
  overflow-y: auto;
}

.document-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.document-item:hover {
  border-color: #ffb347;
  box-shadow: 0 2px 8px rgba(255, 179, 71, 0.1);
}

.document-item.active {
  border-color: #ffb347;
  background: #fff3e0;
}

.document-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  flex: 1;
}

.document-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.document-meta span {
  font-size: 12px;
  color: #999;
}

.btn-delete-small {
  padding: 4px 8px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  line-height: 1;
}

.btn-delete-small:hover {
  background: #d32f2f;
}

.knowledge-panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.panel-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  font-size: 16px;
  color: #333;
  margin: 0;
}

.btn-add-small {
  padding: 8px 16px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-small:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.knowledge-list {
  flex: 1;
  max-height: 500px;
  overflow-y: auto;
}

.knowledge-item {
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  margin-bottom: 12px;
  background: #f9f9f9;
}

.knowledge-content {
  font-size: 14px;
  color: #333;
  margin-bottom: 12px;
  line-height: 1.5;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.knowledge-meta span {
  font-size: 12px;
  color: #999;
}

.empty-panel {
  background: white;
  border-radius: 12px;
  padding: 60px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h4 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 14px;
  color: #999;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.btn-page {
  padding: 8px 16px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-page:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

.dialog-overlay {
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

.dialog {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 500px;
  max-width: 90%;
}

.dialog h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 20px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-cancel {
  background: #f5f5f5;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .panel-header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
