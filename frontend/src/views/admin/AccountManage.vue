<template>
  <div class="admin-page">
    <h2>账号权限管理</h2>
    
    <div class="account-list">
      <div class="list-header">
        <h3>系统账号</h3>
        <button class="btn-primary" @click="showAddModal = true">+ 新增账号</button>
      </div>
      
      <table>
        <thead>
          <tr>
            <th>用户名</th>
            <th>姓名</th>
            <th>角色</th>
            <th>状态</th>
            <th>最后登录</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="account in accounts" :key="account.id">
            <td>{{ account.username }}</td>
            <td>{{ account.name }}</td>
            <td>
              <span class="role-badge" :class="account.role">
                {{ account.role === 'admin' ? '管理员' : '客服' }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="account.status">
                {{ account.status === 'active' ? '正常' : '禁用' }}
              </span>
            </td>
            <td>{{ account.lastLogin || '从未登录' }}</td>
            <td>
              <button class="btn-edit" @click="editAccount(account)">编辑</button>
              <button 
                class="btn-toggle" 
                :class="account.status"
                @click="toggleStatus(account)"
              >
                {{ account.status === 'active' ? '禁用' : '启用' }}
              </button>
              <button class="btn-delete" @click="deleteAccount(account.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="login-config">
      <h3>登录配置</h3>
      <div class="config-form">
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="loginConfig.allowRemember" />
            <span>允许记住密码</span>
          </label>
        </div>
        <div class="form-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="loginConfig.requireCaptcha" />
            <span>登录需要验证码</span>
          </label>
        </div>
        <div class="form-group">
          <label>最大登录失败次数</label>
          <input v-model.number="loginConfig.maxFailedAttempts" type="number" min="1" max="10" />
        </div>
        <div class="form-group">
          <label>登录会话有效期(小时)</label>
          <input v-model.number="loginConfig.sessionTimeout" type="number" min="1" max="72" />
        </div>
      </div>
      <button class="btn-primary" @click="saveLoginConfig">保存配置</button>
    </div>
    
    <!-- 新增/编辑账号弹窗 -->
    <div v-if="showAddModal || editingAccount" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingAccount ? '编辑账号' : '新增账号' }}</h3>
        
        <div class="form-group">
          <label>用户名</label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名"
            :disabled="editingAccount"
          />
        </div>
        
        <div class="form-group">
          <label>姓名</label>
          <input v-model="form.name" type="text" placeholder="请输入姓名" />
        </div>
        
        <div class="form-group">
          <label>密码 {{ editingAccount ? '(留空则不修改)' : '' }}</label>
          <input v-model="form.password" type="password" placeholder="请输入密码" />
        </div>
        
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" />
        </div>
        
        <div class="form-group">
          <label>角色</label>
          <select v-model="form.role">
            <option value="admin">管理员</option>
            <option value="agent">客服</option>
          </select>
        </div>
        
        <div class="modal-actions">
          <button class="btn-primary" @click="saveAccount">保存</button>
          <button class="btn-secondary" @click="closeModal">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const accounts = ref([
  {
    id: 1,
    username: 'admin',
    name: '系统管理员',
    role: 'admin',
    status: 'active',
    lastLogin: '2024-03-01 14:30'
  },
  {
    id: 2,
    username: 'agent01',
    name: '客服小张',
    role: 'agent',
    status: 'active',
    lastLogin: '2024-03-01 10:15'
  }
])

const loginConfig = reactive({
  allowRemember: true,
  requireCaptcha: false,
  maxFailedAttempts: 5,
  sessionTimeout: 24
})

const showAddModal = ref(false)
const editingAccount = ref(null)

const form = reactive({
  username: '',
  name: '',
  password: '',
  confirmPassword: '',
  role: 'agent'
})

function editAccount(account) {
  editingAccount.value = account
  form.username = account.username
  form.name = account.name
  form.role = account.role
  form.password = ''
  form.confirmPassword = ''
}

function closeModal() {
  showAddModal.value = false
  editingAccount.value = null
  form.username = ''
  form.name = ''
  form.password = ''
  form.confirmPassword = ''
  form.role = 'agent'
}

function saveAccount() {
  if (!form.username || !form.name) {
    window.showMessage('请填写完整信息', 'warning')
    return
  }
  
  if (!editingAccount.value && !form.password) {
    window.showMessage('请输入密码', 'warning')
    return
  }
  
  if (form.password && form.password !== form.confirmPassword) {
    window.showMessage('两次输入的密码不一致', 'warning')
    return
  }
  
  if (editingAccount.value) {
    editingAccount.value.name = form.name
    editingAccount.value.role = form.role
    if (form.password) {
      console.log('修改密码:', form.password)
    }
  } else {
    accounts.value.push({
      id: Date.now(),
      username: form.username,
      name: form.name,
      role: form.role,
      status: 'active',
      lastLogin: null
    })
  }
  
  closeModal()
}

function toggleStatus(account) {
  account.status = account.status === 'active' ? 'disabled' : 'active'
}

function deleteAccount(id) {
  if (confirm('确定要删除这个账号吗？')) {
    accounts.value = accounts.value.filter(a => a.id !== id)
  }
}

function saveLoginConfig() {
  localStorage.setItem('loginConfig', JSON.stringify(loginConfig))
  window.showMessage('登录配置已保存', 'success')
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

.account-list {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.list-header h3 {
  font-size: 16px;
  color: #333;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  text-align: left;
  padding: 12px;
  border-bottom: 1px solid #eee;
}

th {
  font-weight: 500;
  color: #666;
  font-size: 13px;
}

td {
  font-size: 14px;
  color: #333;
}

.role-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.role-badge.admin {
  background: #e3f2fd;
  color: #1565c0;
}

.role-badge.agent {
  background: #f3e5f5;
  color: #7b1fa2;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.disabled {
  background: #ffebee;
  color: #c62828;
}

.btn-edit,
.btn-toggle,
.btn-delete {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  border: none;
  margin-right: 6px;
}

.btn-edit {
  background: #ffb347;
  color: white;
}

.btn-toggle {
  background: #ff9800;
  color: white;
}

.btn-toggle.active {
  background: #ff5722;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.login-config {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.login-config h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
}

.config-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
}

.form-group input {
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

.btn-primary {
  padding: 12px 24px;
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
  width: 400px;
}

.modal h3 {
  margin-bottom: 20px;
  color: #333;
}

.modal .form-group {
  margin-bottom: 16px;
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
