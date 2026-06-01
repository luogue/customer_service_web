<template>
  <Teleport to="body">
    <div v-if="visible" :class="['message-toast', type]">
      {{ message }}
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')
const type = ref('success')

let timer = null

function show(msg, msgType = 'success', duration = 3000) {
  if (timer) {
    clearTimeout(timer)
  }
  message.value = msg
  type.value = msgType
  visible.value = true
  
  timer = setTimeout(() => {
    visible.value = false
  }, duration)
}

defineExpose({ show })
</script>

<style scoped>
.message-toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  z-index: 9999;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.message-toast.success {
  background: #67c23a;
  color: white;
}

.message-toast.error {
  background: #f56c6c;
  color: white;
}

.message-toast.warning {
  background: #e6a23c;
  color: white;
}

.message-toast.info {
  background: #909399;
  color: white;
}
</style>