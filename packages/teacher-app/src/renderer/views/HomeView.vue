<template>
  <div class="home">
    <el-header class="header">
      <h1>Network Control 教师端</h1>
      <div class="actions">
        <el-button type="success" @click="setAll('normal')">全部允许上网</el-button>
        <el-button type="warning" @click="setAll('whitelist')">启动白名单</el-button>
        <el-button type="info" @click="setAll('blacklist')">启动黑名单</el-button>
        <el-button type="danger" @click="setAll('disconnect')">禁止上网</el-button>
      </div>
    </el-header>

    <el-main class="main">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card>
            <template #header>
              <span>学生机列表</span>
              <el-button text @click="loadMachines">刷新</el-button>
            </template>
            <el-table :data="store.machines" v-loading="store.loading" stripe>
              <el-table-column prop="ip" label="IP 地址" width="140" />
              <el-table-column prop="hostname" label="主机名" width="160" />
              <el-table-column prop="mode" label="当前状态" width="120">
                <template #default="{ row }">
                  <el-tag :type="modeType(row.mode)">{{ modeText(row.mode) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="online" label="在线" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.online ? 'success' : 'info'">
                    {{ row.online ? '在线' : '离线' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" min-width="220">
                <template #default="{ row }">
                  <el-button size="small" @click="setMachine(row.ip, 'normal')">允许</el-button>
                  <el-button size="small" type="warning" @click="setMachine(row.ip, 'whitelist')">白名单</el-button>
                  <el-button size="small" type="danger" @click="setMachine(row.ip, 'disconnect')">断网</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card>
            <template #header>
              <span>规则管理</span>
            </template>
            <el-tabs v-model="activeTab">
              <el-tab-pane label="白名单" name="whitelist">
                <el-input v-model="newWhitelist" placeholder="输入域名，如 *.example.com" @keyup.enter="addRule('whitelist')">
                  <template #append>
                    <el-button @click="addRule('whitelist')">添加</el-button>
                  </template>
                </el-input>
                <el-table :data="store.whitelist" size="small" class="rule-table">
                  <el-table-column prop="domain" label="域名" />
                  <el-table-column width="60">
                    <template #default="{ row }">
                      <el-button link type="danger" @click="deleteRule('whitelist', row.id)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
              <el-tab-pane label="黑名单" name="blacklist">
                <el-input v-model="newBlacklist" placeholder="输入域名" @keyup.enter="addRule('blacklist')">
                  <template #append>
                    <el-button @click="addRule('blacklist')">添加</el-button>
                  </template>
                </el-input>
                <el-table :data="store.blacklist" size="small" class="rule-table">
                  <el-table-column prop="domain" label="域名" />
                  <el-table-column width="60">
                    <template #default="{ row }">
                      <el-button link type="danger" @click="deleteRule('blacklist', row.id)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </el-tab-pane>
            </el-tabs>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../store/app'
import { api } from '../api'

const store = useAppStore()
const activeTab = ref('whitelist')
const newWhitelist = ref('')
const newBlacklist = ref('')

const modeMap = {
  normal: { text: '正常', type: 'success' },
  whitelist: { text: '白名单', type: 'warning' },
  blacklist: { text: '黑名单', type: 'info' },
  disconnect: { text: '断网', type: 'danger' },
}

const modeText = (mode) => modeMap[mode]?.text || mode
const modeType = (mode) => modeMap[mode]?.type || ''

async function loadMachines() {
  store.loading = true
  const res = await api.getMachines()
  if (res.ok) store.machines = res.data.machines
  store.loading = false
}

async function loadRules() {
  const res = await api.getRules()
  if (res.ok) {
    store.whitelist = res.data.whitelist
    store.blacklist = res.data.blacklist
  }
}

async function setAll(mode) {
  const res = await api.setNetwork(mode)
  if (res.ok) {
    ElMessage.success(`已设置全部学生机为：${modeText(mode)}`)
    await loadMachines()
  } else {
    ElMessage.error('设置失败')
  }
}

async function setMachine(ip, mode) {
  const res = await api.setNetwork(mode, [ip])
  if (res.ok) {
    ElMessage.success(`已设置 ${ip} 为：${modeText(mode)}`)
    await loadMachines()
  } else {
    ElMessage.error('设置失败')
  }
}

async function addRule(listType) {
  const value = listType === 'whitelist' ? newWhitelist.value : newBlacklist.value
  if (!value.trim()) return
  const res = await api.addRule(listType, value.trim())
  if (res.ok) {
    ElMessage.success('添加成功')
    if (listType === 'whitelist') newWhitelist.value = ''
    else newBlacklist.value = ''
    await loadRules()
  } else {
    ElMessage.error('添加失败')
  }
}

async function deleteRule(listType, id) {
  const res = await api.deleteRule(listType, id)
  if (res.ok) {
    ElMessage.success('删除成功')
    await loadRules()
  } else {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadMachines()
  loadRules()
  setInterval(loadMachines, 5000)
})
</script>

<style scoped>
.home {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}
.header h1 {
  margin: 0;
  font-size: 20px;
}
.main {
  flex: 1;
  overflow: auto;
  background: #f5f7fa;
}
.rule-table {
  margin-top: 12px;
}
</style>
