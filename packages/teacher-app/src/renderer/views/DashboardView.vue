<template>
  <div class="dashboard">
    <h2>控制面板</h2>

    <el-row :gutter="20" class="actions">
      <el-col :span="6">
        <el-button type="success" size="large" @click="store.enableAll" :loading="store.loading">
          全部开网
        </el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="danger" size="large" @click="store.disableAll" :loading="store.loading">
          全部断网
        </el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="primary" size="large" @click="store.setMode('whitelist')" :loading="store.loading">
          全部白名单
        </el-button>
      </el-col>
      <el-col :span="6">
        <el-button type="warning" size="large" @click="store.setMode('blacklist')" :loading="store.loading">
          全部黑名单
        </el-button>
      </el-col>
    </el-row>

    <el-divider />

    <div class="scan-bar">
      <el-input v-model="scanSubnet" placeholder="192.168.1.0/24" style="width: 220px; margin-right: 10px;" />
      <el-button @click="doScan" :loading="scanning">扫描网段</el-button>
      <el-button @click="store.fetchMachines">刷新列表</el-button>
    </div>

    <el-table :data="store.machines" style="width: 100%" v-loading="store.loading" border>
      <el-table-column prop="ip" label="IP" width="140" />
      <el-table-column prop="hostname" label="主机名" width="160" />
      <el-table-column prop="mac" label="MAC" width="160" />
      <el-table-column prop="mode" label="当前模式" width="120">
        <template #default="{ row }">
          <el-tag :type="modeType(row.mode)">{{ modeLabel(row.mode) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="online" label="在线" width="80">
        <template #default="{ row }">
          <el-tag :type="row.online ? 'success' : 'info'">{{ row.online ? '在线' : '离线' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_heartbeat" label="最后心跳" width="180">
        <template #default="{ row }">
          {{ row.last_heartbeat ? new Date(row.last_heartbeat * 1000).toLocaleString() : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="260">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="store.enableSingle(row.ip)">开网</el-button>
          <el-button size="small" type="danger" @click="store.disableSingle(row.ip)">断网</el-button>
          <el-button size="small" type="primary" @click="store.setMode('whitelist', [row.ip])">白名单</el-button>
          <el-button size="small" type="warning" @click="store.setMode('blacklist', [row.ip])">黑名单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="scanVisible" title="扫描结果" width="400px">
      <p>发现 {{ scanResults.length }} 台机器：</p>
      <el-tag v-for="ip in scanResults" :key="ip" style="margin: 4px;">{{ ip }}</el-tag>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'

const store = useTeacherStore()
const scanSubnet = ref('192.168.1.0/24')
const scanning = ref(false)
const scanVisible = ref(false)
const scanResults = ref<string[]>([])

let timer: number | undefined

onMounted(() => {
  store.fetchMachines()
  timer = window.setInterval(() => store.fetchMachines(), 3000)
})

onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})

async function doScan() {
  scanning.value = true
  try {
    const res = await store.scanSubnet(scanSubnet.value)
    scanResults.value = res.ips
    scanVisible.value = true
  } finally {
    scanning.value = false
  }
}

function modeLabel(mode: string) {
  const map: Record<string, string> = {
    normal: '正常',
    whitelist: '白名单',
    blacklist: '黑名单',
    disconnect: '断网',
  }
  return map[mode] || mode
}

function modeType(mode: string) {
  const map: Record<string, any> = {
    normal: 'success',
    whitelist: 'primary',
    blacklist: 'warning',
    disconnect: 'danger',
  }
  return map[mode] || 'info'
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.actions {
  margin-bottom: 20px;
}
.actions .el-button {
  width: 100%;
}
.scan-bar {
  margin-bottom: 20px;
}
</style>
