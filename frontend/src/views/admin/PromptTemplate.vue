<template>
  <div class="admin-page">
    <h2>Prompt 模板管理</h2>
    
    <div class="template-list">
      <div 
        v-for="template in templates" 
        :key="template.id"
        class="template-card"
        :class="{ active: template.is_default === 1 }"
      >
        <div class="template-header">
          <div class="template-info">
            <h3>{{ template.template_name }}</h3>
            <span class="badge" :class="template.is_default === 1 ? 'active' : 'inactive'">
                {{ template.is_default === 1 ? '默认' : '非默认' }}
              </span>
          </div>
          <div class="template-actions">
            <button 
              class="btn-toggle"
              :class="template.is_default === 1 ? 'stop' : 'start'"
              @click="toggleDefaultTemplate(template)"
            >
              {{ template.is_default === 1 ? '取消默认' : '设为默认' }}
            </button>
            <button class="btn-edit" @click="editTemplate(template)">编辑</button>
            <button class="btn-delete" @click="deleteTemplate(template.id)">
              {{ template.is_default === 1 ? '不可删除' : '删除' }}
            </button>
          </div>
        </div>
        <div class="template-content">
          <pre>{{ template.template_content }}</pre>
        </div>
      </div>
    </div>
    
    <button class="btn-add" @click="showAddModal = true">
      + 新增模板
    </button>
    
    <!-- 新增/编辑弹窗 -->
    <div v-if="showAddModal || editingTemplate" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingTemplate ? '编辑模板' : '新增模板' }}</h3>
        <div class="form-group">
          <label>模板名称</label>
          <input v-model="form.template_name" type="text" placeholder="请输入模板名称" />
        </div>
        <div class="form-group">
          <label>提示词内容</label>
          <textarea 
            v-model="form.template_content" 
            rows="10" 
            placeholder="请输入提示词内容"
          ></textarea>
        </div>
        <div class="form-group">
          <label>
            <input v-model="form.is_default" type="checkbox" />
            设为默认模板
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn-primary" @click="saveTemplate">保存</button>
          <button class="btn-secondary" @click="closeModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const templates = ref([])
const showAddModal = ref(false)
const editingTemplate = ref(null)

const form = reactive({
  template_name: '',
  template_content: '',
  is_default: 0
})

// 获取所有模板
async function fetchTemplates() {
  try {
    const response = await fetch('/api/prompt/templates')
    if (response.ok) {
      const data = await response.json()
      templates.value = data
    } else {
      console.error('获取模板失败:', response.statusText)
    }
  } catch (error) {
    console.error('获取模板失败:', error)
  }
}

// 新增模板
async function createTemplate() {
  try {
    const response = await fetch('/api/prompt/templates', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    })
    if (response.ok) {
      await fetchTemplates()
      return true
    } else {
      const error = await response.json()
      alert('创建模板失败: ' + (error.detail || '未知错误'))
      return false
    }
  } catch (error) {
    console.error('创建模板失败:', error)
    alert('创建模板失败: ' + error.message)
    return false
  }
}

// 更新模板
async function updateTemplate(id) {
  try {
    const response = await fetch(`/api/prompt/templates/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form)
    })
    if (response.ok) {
      await fetchTemplates()
      return true
    } else {
      const error = await response.json()
      alert('更新模板失败: ' + (error.detail || '未知错误'))
      return false
    }
  } catch (error) {
    console.error('更新模板失败:', error)
    alert('更新模板失败: ' + error.message)
    return false
  }
}

// 删除模板
async function deleteTemplate(id) {
  // 检查是否是默认模板
  const template = templates.value.find(t => t.id === id)
  if (template && template.is_default === 1) {
    alert('不能删除默认模板')
    return
  }
  
  if (confirm('确定要删除这个模板吗？')) {
    try {
      const response = await fetch(`/api/prompt/templates/${id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        await fetchTemplates()
      } else {
        const error = await response.json()
        alert('删除模板失败: ' + (error.detail || '未知错误'))
      }
    } catch (error) {
      console.error('删除模板失败:', error)
      alert('删除模板失败: ' + error.message)
    }
  }
}

// 设为默认模板
async function toggleDefaultTemplate(template) {
  if (template.is_default === 1) {
    // 取消默认，不允许
    alert('至少需要一个默认模板')
    return
  }
  
  // 设为默认
  form.template_name = template.template_name
  form.template_content = template.template_content
  form.is_default = 1
  await updateTemplate(template.id)
}

function editTemplate(template) {
  editingTemplate.value = template
  form.template_name = template.template_name
  form.template_content = template.template_content
  form.is_default = template.is_default
}

function closeModal() {
  showAddModal.value = false
  editingTemplate.value = null
  form.template_name = ''
  form.template_content = ''
  form.is_default = 0
}

async function saveTemplate() {
  if (!form.template_name || !form.template_content) {
    alert('请填写模板名称和内容')
    return
  }
  
  let success = false
  if (editingTemplate.value) {
    success = await updateTemplate(editingTemplate.value.id)
  } else {
    success = await createTemplate()
  }
  
  if (success) {
    closeModal()
  }
}

// 组件挂载时获取模板
onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
.admin-page {
  padding: 24px;
}

.admin-page h2 {
  margin-bottom: 24px;
  color: #333;
}

.template-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.template-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
}

.template-card.active {
  border-color: #ffb347;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.template-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.template-info h3 {
  font-size: 16px;
  color: #333;
}

.badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.badge.active {
  background: #e8f5e9;
  color: #4caf50;
}

.badge.inactive {
  background: #f5f5f5;
  color: #999;
}

.template-actions {
  display: flex;
  gap: 8px;
}

.template-actions button {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-toggle {
  color: white;
}

.btn-toggle.start {
  background: #4caf50;
}

.btn-toggle.stop {
  background: #ff9800;
}

.btn-edit {
  background: #ffb347;
  color: white;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.template-content pre {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.btn-add {
  margin-top: 20px;
  width: 100%;
  padding: 14px;
  background: white;
  border: 2px dashed #ddd;
  border-radius: 12px;
  color: #ffb347;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  border-color: #ffb347;
  background: #f8f9ff;
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
  font-family: inherit;
}

.form-group textarea {
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.btn-primary {
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}
</style>
