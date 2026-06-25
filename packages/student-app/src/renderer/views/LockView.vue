<template>
  <div class="lock-screen">
    <div class="lock-content">
      <el-icon size="80" color="#f56c6c"><Warning /></el-icon>
      <h1>网络已断开</h1>
      <p>请插好网线或联系老师解锁</p>
      <p class="countdown">{{ countdown }} 秒后自动关机</p>
      <el-button type="primary" size="large" @click="unlock">我已插好网线</el-button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Warning } from '@element-plus/icons-vue'

const countdown = ref(60)
let timer = null

onMounted(() => {
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      // 调用关机逻辑（开发阶段先隐藏窗口）
      if (window.electronAPI) window.electronAPI.hideLock()
    }
  }, 1000)
})

function unlock() {
  // 实际应检查网线是否恢复
  if (window.electronAPI) window.electronAPI.hideLock()
}
</script>

<style scoped>
.lock-screen {
  height: 100vh;
  width: 100vw;
  background: #000;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  user-select: none;
}
.lock-content h1 {
  font-size: 48px;
  margin: 20px 0;
}
.lock-content p {
  font-size: 24px;
  margin: 10px 0;
}
.countdown {
  color: #f56c6c;
  font-size: 32px;
  margin: 30px 0;
}
</style>
