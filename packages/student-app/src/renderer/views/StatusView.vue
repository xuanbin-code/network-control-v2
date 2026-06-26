<template>
  <div class="status-page">
    <h2>当前状态</h2>

    <el-card>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="连接状态">
          <el-tag :type="store.status.connected ? 'success' : 'danger'">
            {{ store.status.connected ? '已连接教师端' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="当前模式">
          <el-tag :type="modeType" size="large">{{ modeLabel }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="教师端地址">{{ store.status.controller_url || '-' }}</el-descriptions-item>
        <el-descriptions-item label="本机 IP">{{ store.status.controller_ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="主机名">{{ store.status.hostname || '-' }}</el-descriptions-item>
        <el-descriptions-item label="MAC">{{ store.status.mac || '-' }}</el-descriptions-item>
        <el-descriptions-item label="规则数量">{{ store.status.rule_count || 0 }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-row :gutter="20" class="actions">
      <el-col :span="6">
        <el-button type="success" size="large" @click="store.setMode('normal')">开网</el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="danger" size="large" @click="store.setMode('disconnect')">断网</el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" size="large" @click="store.setMode('whitelist')">白名单</el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="warning" size="large" @click="store.setMode('blacklist')">黑名单</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed } from 'vue'
import { useStudentStore } from '@/stores/student'

const store = useStudentStore()
let timer: number | undefined

onMounted(() => {
  store.fetchStatus()
  timer = window.setInterval(() => store.fetchStatus(), 3000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})

const modeLabel = computed(() => {
  const map: Record<string, string> = {
    normal: '正常上网',
    whitelist: '白名单过滤',
    blacklist: '黑名单过滤',
    disconnect: '已断网',
  }
  return map[store.status.mode] || store.status.mode
})

const modeType = computed(() => {
  const map: Record<string, any> = {
    normal: 'success',
    whitelist: 'primary',
    blacklist: 'warning',
    disconnect: 'danger',
  }
  return map[store.status.mode] || 'info'
})
</script>

<style scoped>
.status-page {
  padding: 20px;
}
.actions {
  margin-top: 20px;
}
.actions .el-button {
  width: 100%;
}
</style>
