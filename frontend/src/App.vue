<template>
  <div class="app">
    <router-view />
    <MessageToast ref="messageToast" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import MessageToast from './components/MessageToast.vue'

const messageToast = ref(null)

window.showMessage = (message, type = 'success') => {
  if (messageToast.value) {
    messageToast.value.show(message, type)
  }
}
</script>

<style scoped>
.app {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 320px;
  overflow-x: auto;
}
</style>