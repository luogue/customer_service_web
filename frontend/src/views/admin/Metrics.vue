<template>
  <div class="metrics-page">
    <h2>AI 客服指标统计</h2>
    
    <div class="metrics-summary">
      <div class="metric-card">
        <div class="metric-icon">🎯</div>
        <div class="metric-info">
          <div class="metric-label">意图识别准确率</div>
          <div class="metric-value">{{ metrics.intent_accuracy }}%</div>
          <div class="metric-desc">答对次数 / 总请求数</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">✅</div>
        <div class="metric-info">
          <div class="metric-label">流程完成率</div>
          <div class="metric-value">{{ metrics.completion_rate }}%</div>
          <div class="metric-desc">正常走完业务的比例</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">💡</div>
        <div class="metric-info">
          <div class="metric-label">上下文命中率</div>
          <div class="metric-value">{{ metrics.context_hit_rate }}%</div>
          <div class="metric-desc">靠上下文直接处理的比例</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-info">
          <div class="metric-label">转人工率</div>
          <div class="metric-value">{{ metrics.transfer_rate }}%</div>
          <div class="metric-desc">最终转人工的问题比例</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">⚡</div>
        <div class="metric-info">
          <div class="metric-label">单轮平均响应时长</div>
          <div class="metric-value">{{ metrics.avg_response_time }}ms</div>
          <div class="metric-desc">AI 从接收消息到返回结果的时间</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-info">
          <div class="metric-label">总测试次数</div>
          <div class="metric-value">{{ metrics.total_count }}</div>
          <div class="metric-desc">累计测试请求数</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">✓</div>
        <div class="metric-info">
          <div class="metric-label">正确答案率</div>
          <div class="metric-value">{{ metrics.correct_answer_rate }}%</div>
          <div class="metric-desc">基于 {{ metrics.labeled_count }} 条人工标注数据</div>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">👻</div>
        <div class="metric-info">
          <div class="metric-label">幻觉率</div>
          <div class="metric-value">{{ metrics.hallucination_rate }}%</div>
          <div class="metric-desc">基于 {{ metrics.hallucination_labeled_count }} 条人工标注数据</div>
        </div>
      </div>
    </div>
    
    <div class="metrics-actions">
      <button class="btn-refresh" @click="loadMetrics">
        🔄 刷新数据
      </button>
      <button class="btn-reset" @click="resetMetrics">
        🗑️ 重置数据
      </button>
    </div>
    
    <div class="metrics-explanation">
      <h3>指标说明</h3>
      <div class="explanation-item">
        <strong>意图识别准确率</strong>：答对次数 / 总请求数。衡量 AI 对用户意图的识别准确性。
      </div>
      <div class="explanation-item">
        <strong>流程完成率</strong>：正常走完业务（查单 / 退款 / 换货）的比例。衡量 AI 完成业务流程的能力。
      </div>
      <div class="explanation-item">
        <strong>上下文命中率</strong>：靠上下文直接处理、不用重识别的比例。衡量 AI 利用上下文信息的能力。
      </div>
      <div class="explanation-item">
        <strong>转人工率</strong>：多少问题最终转人工。衡量 AI 独立解决问题的能力。
      </div>
      <div class="explanation-item">
        <strong>单轮平均响应时长</strong>：用户发 "查订单"，AI 从接收消息到返回结果的时间。衡量 AI 的响应速度。
      </div>
      <div class="explanation-item">
        <strong>总测试次数</strong>：累计测试请求数。建议测试 30-50 次以获得可靠的指标数据。
      </div>
      <div class="explanation-item">
        <strong>正确答案率</strong>：AI 回答正确的比例（需要人工标注）。衡量 AI 回答内容的准确性。
      </div>
      <div class="explanation-item">
        <strong>幻觉率</strong>：AI 产生幻觉（编造事实）的比例（需要人工标注）。衡量 AI 回答的可靠性。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const metrics = ref({
  total_count: 0,
  intent_accuracy: 0,
  completion_rate: 0,
  context_hit_rate: 0,
  transfer_rate: 0,
  avg_response_time: 0,
  correct_answer_rate: 0,
  hallucination_rate: 0,
  labeled_count: 0,
  hallucination_labeled_count: 0
})

const loading = ref(false)

async function loadMetrics() {
  try {
    loading.value = true
    const response = await fetch('http://localhost:8004/api/chat/metrics')
    const data = await response.json()
    
    if (data.success) {
      metrics.value = data.data
    }
  } catch (error) {
    console.error('加载指标失败:', error)
    window.showMessage('加载指标失败', 'error')
  } finally {
    loading.value = false
  }
}

async function resetMetrics() {
  if (confirm('确定要重置所有指标数据吗？')) {
    try {
      const response = await fetch('http://localhost:8004/api/chat/metrics/reset', {
        method: 'POST'
      })
      
      if (response.ok) {
        window.showMessage('指标数据已重置', 'success')
        await loadMetrics()
      }
    } catch (error) {
      console.error('重置指标失败:', error)
      window.showMessage('重置指标失败', 'error')
    }
  }
}

onMounted(() => {
  loadMetrics()
})
</script>

<style scoped>
.metrics-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.metrics-page h2 {
  margin-bottom: 20px;
  color: #333;
}

.metrics-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.metric-icon {
  font-size: 40px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 50%;
}

.metric-info {
  flex: 1;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.metric-value {
  font-size: 28px;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 5px;
}

.metric-desc {
  font-size: 12px;
  color: #999;
}

.metrics-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.btn-refresh,
.btn-reset {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-refresh {
  background: #2196F3;
  color: white;
}

.btn-refresh:hover {
  background: #1976D2;
}

.btn-reset {
  background: #f44336;
  color: white;
}

.btn-reset:hover {
  background: #d32f2f;
}

.metrics-explanation {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metrics-explanation h3 {
  margin-bottom: 15px;
  color: #333;
}

.explanation-item {
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  color: #666;
  line-height: 1.6;
}

.explanation-item:last-child {
  border-bottom: none;
}

.explanation-item strong {
  color: #333;
}
</style>
