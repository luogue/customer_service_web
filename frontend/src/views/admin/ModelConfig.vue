<template>
  <div class="admin-page">
    <h2>模型配置</h2>
    <div class="config-card">
      <div class="form-group">
        <label>选择大模型</label>
        <select v-model="config.model">
          <option value="glm-4">智谱 GLM-4</option>
          <option value="glm-4-flash">智谱 GLM-4-Flash</option>
          <option value="glm-4-air">智谱 GLM-4-Air</option>
          <option value="gpt-4">OpenAI GPT-4</option>
          <option value="gpt-3.5-turbo">OpenAI GPT-3.5</option>
        </select>
      </div>
      
      <div class="form-group">
        <label>API 密钥</label>
        <input 
          v-model="config.apiKey" 
          type="password" 
          placeholder="请输入API密钥"
        />
      </div>
      
      <div class="form-row">
        <div class="form-group">
          <label>超时时间 (秒)</label>
          <input 
            v-model.number="config.timeout" 
            type="number" 
            min="1" 
            max="60"
          />
        </div>
        
        <div class="form-group">
          <label>重试次数</label>
          <input 
            v-model.number="config.retryCount" 
            type="number" 
            min="0" 
            max="5"
          />
        </div>
      </div>
      
      <div class="form-group">
        <label>温度 (Temperature)</label>
        <input 
          v-model.number="config.temperature" 
          type="range" 
          min="0" 
          max="2" 
          step="0.1"
        />
        <span class="range-value">{{ config.temperature }}</span>
      </div>
      
      <div class="form-group">
        <label>最大Token数</label>
        <input 
          v-model.number="config.maxTokens" 
          type="number" 
          min="100" 
          max="4096"
        />
      </div>
      
      <div class="actions">
        <button class="btn-primary" @click="saveConfig">保存配置</button>
        <button class="btn-secondary" @click="testConnection">测试连接</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const config = ref({
  model: 'glm-4',
  apiKey: '',
  timeout: 30,
  retryCount: 3,
  temperature: 0.7,
  maxTokens: 2000
})

function saveConfig() {
  localStorage.setItem('modelConfig', JSON.stringify(config.value))
  window.showMessage('配置已保存', 'success')
}

function testConnection() {
  window.showMessage('正在测试连接...', 'info')
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

.config-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  max-width: 300px;
}

.form-group select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  width: auto;
  min-width: 200px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #ffb347;
}

.form-row {
  display: flex;
  gap: 32px;
  flex-wrap: nowrap;
}

.form-row .form-group {
  min-width: 250px;
  text-align: left;
}

.form-row .form-group input {
  width: 200px;
}

.range-value {
  margin-left: 12px;
  color: #ffb347;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.btn-secondary:hover {
  background: #eee;
}
</style>
