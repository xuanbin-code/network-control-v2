<template>
  <div class="config">
    <el-card class="box-card">
      <template #header>
        <span>学生端设置</span>
      </template>

      <el-form label-width="120px">
        <el-form-item label="教师端地址">
          <el-input v-model="form.controller_url" placeholder="ws://192.168.1.100:8765" />
        </el-form-item>
        <el-form-item label="上游 DNS">
          <el-input v-model="form.upstream_dns" placeholder="114.114.114.114" />
        </el-form-item>
        <el-form-item label="当前状态">
          <el-tag :type="statusType">{{ statusText }}</el-tag>
        </el-form-item>
        <el-form-item label="连接状态">
          <el-tag :type="store.status.connected ? 'success' : 'danger'">
            {{ store.status.connected ? '已连接' : '未连接' }}
          </el-tag>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button @click="loadStatus">刷新状态</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../store/app'
import { api } from '../api'

const store = useAppStore()
const form = reactive({
  controller_url: '',
  upstream_dns: '',
})

const modeMap = {
  normal: { text: '正常上网', type: 'success' },
  whitelist: { text: '白名单', type: 'warning' },
  blacklist: { text: '黑名单', type: 'info' },
  disconnect: { text: '已断网', type: 'danger' },
}

const statusText = computed(() => modeMap[store.status.mode]?.text || store.status.mode)
const statusType = computed(() => modeMap[store.status.mode]?.type || '')

async function loadStatus() {
  const res = await api.getStatus()
  if (res.ok) {
    store.status = res.data
  }
}

async function loadConfig() {
  const res = await api.getConfig()
  if (res.ok) {
    store.config = res.data
    form.controller_url = res.data.controller_url || ''
    form.upstream_dns = res.data.upstream_dns || ''
  }
}

async function saveConfig() {
  const res = await api.updateConfig({
    controller_url: form.controller_url,
    upstream_dns: form.upstream_dns,
  })
  if (res.ok) {
    ElMessage.success('配置已保存，重启后生效')
    await loadConfig()
  } else {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadConfig()
  loadStatus()
  setInterval(loadStatus, 5000)
})
</script>

<style scoped>
.config {
  padding: 20px;
}
.box-card {
  max-width: 480px;
  margin: 0 auto;
}
</style>
