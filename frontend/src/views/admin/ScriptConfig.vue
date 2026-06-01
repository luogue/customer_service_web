<template>
  <div class="script-config">
    <h2>话术配置</h2>
    <div class="config-section">
      <div class="form-group">
        <label>欢迎语</label>
        <textarea v-model="welcomeMessage" rows="3" placeholder="请输入欢迎语..."></textarea>
      </div>
      <div class="form-group">
        <label>结束语</label>
        <textarea v-model="endingMessage" rows="3" placeholder="请输入结束语..."></textarea>
      </div>
      <button class="save-btn" @click="saveConfig">保存配置</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const welcomeMessage = ref('您好，欢迎咨询客服，有什么可以帮助您的？')
const endingMessage = ref('感谢您的咨询，祝您生活愉快！')

const saveConfig = () => {
  // 保存配置的逻辑
  console.log('保存话术配置', { welcomeMessage: welcomeMessage.value, endingMessage: endingMessage.value })
  window.showMessage('配置保存成功！', 'success')
}
</script>

<style scoped>
.script-config {
  padding: 24px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-bottom: 24px;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.config-section {
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.5;
}

.save-btn {
  margin-top: 20px;
  padding: 10px 24px;
  background: linear-gradient(135deg, #ffb347 0%, #ff8c00 100%);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.save-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 179, 71, 0.4);
}
</style>