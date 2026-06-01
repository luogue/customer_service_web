<template>
  <div class="admin-page">
    <h2>人工转接配置</h2>
    
    <div class="config-container">
      <!-- 转接触发条件 -->
      <div class="config-section">
        <h3>自动转接触发条件</h3>
        <div class="conditions">
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.triggerOnUnknown" />
            <span>用户连续提问未识别问题超过</span>
            <input 
              v-model.number="config.unknownQuestionCount" 
              type="number" 
              min="1" 
              max="10"
              class="small-input"
            />
            <span>次</span>
          </label>
          
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.triggerOnNegative" />
            <span>用户表达负面情绪（如：生气、不满、投诉）</span>
          </label>
          
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.triggerOnKeyword" />
            <span>用户消息包含转接关键词</span>
          </label>
          
          <div v-if="config.triggerOnKeyword" class="keywords-input">
            <input 
              v-model="transferKeywords" 
              type="text" 
              placeholder="输入关键词，用逗号分隔（如：人工客服,转人工）"
            />
          </div>
          
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.triggerOnTimeout" />
            <span>用户长时间未得到满意答复（超过</span>
            <input 
              v-model.number="config.timeoutMinutes" 
              type="number" 
              min="1" 
              max="30"
              class="small-input"
            />
            <span>分钟）</span>
          </label>
          
          <label class="checkbox-item">
            <input type="checkbox" v-model="config.triggerOnComplex" />
            <span>问题复杂度超过AI处理范围</span>
          </label>
        </div>
      </div>
      
      <!-- 转接提示语 -->
      <div class="config-section">
        <h3>转接提示语配置</h3>
        <div class="form-group">
          <label>转接前提示语</label>
          <textarea 
            v-model="config.beforeTransferMessage" 
            rows="2"
            placeholder="转接前向用户显示的提示"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>转接中提示语</label>
          <textarea 
            v-model="config.transferringMessage" 
            rows="2"
            placeholder="正在转接人工客服时显示的提示"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>转接成功提示语</label>
          <textarea 
            v-model="config.transferSuccessMessage" 
            rows="2"
            placeholder="成功转接后显示的提示"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>排队等待提示语</label>
          <textarea 
            v-model="config.queueMessage" 
            rows="2"
            placeholder="需要排队等待时显示的提示"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label>非工作时间提示语</label>
          <textarea 
            v-model="config.offlineMessage" 
            rows="2"
            placeholder="非工作时间无法转接时显示的提示"
          ></textarea>
        </div>
      </div>
      
      <!-- 转接设置 -->
      <div class="config-section">
        <h3>转接设置</h3>
        <div class="form-row">
          <div class="form-group">
            <label>最大排队人数</label>
            <input v-model.number="config.maxQueueSize" type="number" min="1" max="100" />
          </div>
          <div class="form-group">
            <label>转接超时时间 (分钟)</label>
            <input v-model.number="config.transferTimeout" type="number" min="1" max="30" />
          </div>
        </div>
        
        <div class="form-group">
          <label>转接失败处理方式</label>
          <select v-model="config.transferFailAction">
            <option value="continue">继续AI对话</option>
            <option value="leave_message">引导留言</option>
            <option value="callback">预约回电</option>
          </select>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button class="btn-primary" @click="saveConfig">保存配置</button>
      <button class="btn-secondary" @click="resetConfig">重置默认</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const defaultConfig = {
  triggerOnUnknown: true,
  unknownQuestionCount: 3,
  triggerOnNegative: true,
  triggerOnKeyword: true,
  triggerOnTimeout: true,
  timeoutMinutes: 10,
  triggerOnComplex: true,
  beforeTransferMessage: '我理解您的问题比较复杂，为您转接人工客服处理，请稍候..',
  transferringMessage: '正在为您转接人工客服，请稍等...',
  transferSuccessMessage: '已成功为您接入人工客服，请问有什么可以帮助您的？',
  queueMessage: '当前人工客服繁忙，您前面还有 {queueCount} 人排队，请耐心等待...',
  offlineMessage: '当前非工作时间，人工客服不在线。您可以留言，我们会尽快回复您。',
  maxQueueSize: 50,
  transferTimeout: 5,
  transferFailAction: 'leave_message'
}

const config = reactive({ ...defaultConfig })
const transferKeywords = ref('人工,客服,转人工,人工客服')

function saveConfig() {
  const dataToSave = {
    ...config,
    transferKeywords: transferKeywords.value.split(',').map(k => k.trim())
  }
  localStorage.setItem('transferConfig', JSON.stringify(dataToSave))
  window.showMessage('配置已保存', 'success')
}

function resetConfig() {
  if (confirm('确定要重置为默认配置吗？')) {
    Object.assign(config, defaultConfig)
    transferKeywords.value = '人工,客服,转人工,人工客服'
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

.config-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.config-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.config-section h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.conditions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.small-input {
  width: 60px;
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.keywords-input {
  margin-left: 28px;
  margin-top: 8px;
}

.keywords-input input {
  width: 100%;
  max-width: 400px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
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

.form-group textarea {
  resize: vertical;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
