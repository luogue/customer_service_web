<template>
  <div class="admin-page">
    <h2>对话规则配置</h2>
    
    <div class="rules-container">
      <!-- 会话设置 -->
      <div class="rule-section">
        <h3>会话设置</h3>
        <div class="form-row">
          <div class="form-group">
            <label>会话超时时间 (分钟)</label>
            <input v-model.number="rules.sessionTimeout" type="number" min="1" max="60" />
          </div>
          <div class="form-group">
            <label>最大对话轮次</label>
            <input v-model.number="rules.maxRounds" type="number" min="1" max="100" />
          </div>
        </div>
      </div>
      
      <!-- 敏感词管理 -->
      <div class="rule-section">
        <h3>敏感词管理</h3>
        <div class="sensitive-words">
          <div 
            v-for="(word, index) in rules.sensitiveWords" 
            :key="index"
            class="word-tag"
          >
            {{ word }}
            <span class="remove" @click="removeSensitiveWord(index)">×</span>
          </div>
          <div class="add-word">
            <input 
              v-model="newWord" 
              type="text" 
              placeholder="输入敏感词"
              @keyup.enter="addSensitiveWord"
            />
            <button @click="addSensitiveWord">添加</button>
          </div>
        </div>
      </div>
      
      <!-- 违禁拦截动作 -->
      <div class="rule-section">
        <h3>违禁拦截动作</h3>
        <div class="form-group">
          <label>检测到敏感词时的处理方式</label>
          <select v-model="rules.violationAction">
            <option value="warn">仅警告</option>
            <option value="block">拦截消息</option>
            <option value="block_and_notify">拦截并通知管理员</option>
            <option value="ban">封禁用户</option>
          </select>
        </div>
        <div class="form-group">
          <label>警告提示语</label>
          <textarea 
            v-model="rules.warningMessage" 
            rows="2"
            placeholder="请输入检测到敏感词时的提示语"
          ></textarea>
        </div>
      </div>
      
      <!-- 消息频率限制 -->
      <div class="rule-section">
        <h3>消息频率限制</h3>
        <div class="form-row">
          <div class="form-group">
            <label>每分钟最大消息数</label>
            <input v-model.number="rules.maxMessagesPerMinute" type="number" min="1" max="100" />
          </div>
          <div class="form-group">
            <label>连续相同消息限制</label>
            <input v-model.number="rules.maxDuplicateMessages" type="number" min="1" max="10" />
          </div>
        </div>
      </div>
    </div>
    
    <div class="actions">
      <button class="btn-primary" @click="saveRules">保存规则</button>
      <button class="btn-secondary" @click="resetRules">重置默认</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const defaultRules = {
  sessionTimeout: 30,
  maxRounds: 50,
  sensitiveWords: ['脏话', '诈骗', '赌博', '色情'],
  violationAction: 'block_and_notify',
  warningMessage: '您的消息包含不当内容，已被系统拦截。请文明交流。',
  maxMessagesPerMinute: 20,
  maxDuplicateMessages: 3
}

const rules = reactive({ ...defaultRules })
const newWord = ref('')

function addSensitiveWord() {
  if (newWord.value.trim() && !rules.sensitiveWords.includes(newWord.value.trim())) {
    rules.sensitiveWords.push(newWord.value.trim())
    newWord.value = ''
  }
}

function removeSensitiveWord(index) {
  rules.sensitiveWords.splice(index, 1)
}

function saveRules() {
  localStorage.setItem('chatRules', JSON.stringify(rules))
  window.showMessage('规则已保存', 'success')
}

function resetRules() {
  if (confirm('确定要重置为默认规则吗？')) {
    Object.assign(rules, defaultRules)
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

.rules-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rule-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.rule-section h3 {
  font-size: 16px;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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

.sensitive-words {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.word-tag {
  background: #ffebee;
  color: #c62828;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.word-tag .remove {
  cursor: pointer;
  font-weight: bold;
  opacity: 0.7;
}

.word-tag .remove:hover {
  opacity: 1;
}

.add-word {
  display: flex;
  gap: 8px;
}

.add-word input {
  width: 150px;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 20px;
  font-size: 13px;
}

.add-word button {
  padding: 8px 16px;
  background: #ffb347;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
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
