<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">控制面板</h2>

    <div class="flex items-center gap-6 rounded-lg border bg-card p-4 text-sm">
      <div class="flex items-center gap-2">
        <span class="text-muted-foreground">本机 IP</span>
        <Badge variant="default">{{ store.serverInfo.ip || '获取中...' }}</Badge>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-muted-foreground">WebSocket 地址</span>
        <code class="rounded bg-muted px-2 py-0.5 text-xs">{{ store.serverInfo.ws_url || '获取中...' }}</code>
      </div>
    </div>

    <div class="grid grid-cols-4 gap-4">
      <Button variant="default" size="lg" class="w-full" :disabled="store.loading" @click="store.enableAll">
        全部开网
      </Button>
      <Button variant="destructive" size="lg" class="w-full" :disabled="store.loading" @click="store.disableAll">
        全部断网
      </Button>
      <Button variant="secondary" size="lg" class="w-full" :disabled="store.loading" @click="store.setMode('whitelist')">
        全部白名单
      </Button>
      <Button variant="outline" size="lg" class="w-full" :disabled="store.loading" @click="store.setMode('blacklist')">
        全部黑名单
      </Button>
    </div>

    <Separator />

    <div class="flex items-center gap-3">
      <Input v-model="scanSubnet" placeholder="192.168.1.0/24" class="w-[220px]" />
      <Button :disabled="scanning" @click="doScan">扫描网段</Button>
      <Button variant="outline" @click="store.fetchMachines">刷新列表</Button>
    </div>

    <div v-if="store.loading" class="text-sm text-muted-foreground">加载中...</div>
    <Table v-else>
      <TableHeader>
        <TableRow>
          <TableHead class="w-[140px]">IP</TableHead>
          <TableHead class="w-[160px]">主机名</TableHead>
          <TableHead class="w-[160px]">MAC</TableHead>
          <TableHead class="w-[120px]">当前模式</TableHead>
          <TableHead class="w-[80px]">在线</TableHead>
          <TableHead class="w-[180px]">最后心跳</TableHead>
          <TableHead>操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="row in store.machines" :key="row.ip">
          <TableCell>{{ row.ip }}</TableCell>
          <TableCell>{{ row.hostname }}</TableCell>
          <TableCell>{{ row.mac }}</TableCell>
          <TableCell>
            <Badge :variant="modeVariant(row.mode)">{{ modeLabel(row.mode) }}</Badge>
          </TableCell>
          <TableCell>
            <Badge :variant="row.online ? 'default' : 'secondary'">
              {{ row.online ? '在线' : '离线' }}
            </Badge>
          </TableCell>
          <TableCell>
            {{ row.last_heartbeat ? new Date(row.last_heartbeat * 1000).toLocaleString() : '-' }}
          </TableCell>
          <TableCell>
            <div class="flex flex-wrap gap-2">
              <Button size="sm" variant="default" @click="store.enableSingle(row.ip)">开网</Button>
              <Button size="sm" variant="destructive" @click="store.disableSingle(row.ip)">断网</Button>
              <Button size="sm" variant="secondary" @click="store.setMode('whitelist', [row.ip])">白名单</Button>
              <Button size="sm" variant="outline" @click="store.setMode('blacklist', [row.ip])">黑名单</Button>
              <Button size="sm" variant="ghost" @click="openTestDialog(row.ip)">测试</Button>
            </div>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>

    <Dialog v-model:open="scanVisible">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>扫描结果</DialogTitle>
        </DialogHeader>
        <p>发现 {{ scanResults.length }} 台机器：</p>
        <div class="flex flex-wrap gap-2">
          <Badge v-for="ip in scanResults" :key="ip" variant="secondary">{{ ip }}</Badge>
        </div>
      </DialogContent>
    </Dialog>

    <Dialog v-model:open="testVisible">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>发送测试消息</DialogTitle>
          <DialogDescription v-if="testTargetIp">
            目标: {{ testTargetIp }}
          </DialogDescription>
          <DialogDescription v-else>
            目标: 全部在线学生端
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div>
            <Label for="test-message">消息内容</Label>
            <Textarea
              id="test-message"
              v-model="testMessage"
              placeholder="输入要发送的测试消息..."
              class="mt-2"
              rows="4"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" @click="testVisible = false">取消</Button>
            <Button :disabled="!testMessage.trim()" @click="doSendTest">
              {{ sending ? '发送中...' : '发送' }}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

const store = useTeacherStore()
const scanSubnet = ref('192.168.1.0/24')
const scanning = ref(false)
const scanVisible = ref(false)
const scanResults = ref<string[]>([])

const testVisible = ref(false)
const testTargetIp = ref('')
const testMessage = ref('')
const sending = ref(false)

let timer: number | undefined

onMounted(() => {
  store.fetchServerInfo()
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

function openTestDialog(ip: string) {
  testTargetIp.value = ip
  testMessage.value = ''
  testVisible.value = true
}

async function doSendTest() {
  if (!testMessage.value.trim()) return
  sending.value = true
  try {
    const targets = testTargetIp.value ? [testTargetIp.value] : undefined
    await store.testMessage(testMessage.value.trim(), targets)
    testVisible.value = false
  } finally {
    sending.value = false
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

function modeVariant(mode: string) {
  const map: Record<string, any> = {
    normal: 'default',
    whitelist: 'secondary',
    blacklist: 'outline',
    disconnect: 'destructive',
  }
  return map[mode] || 'secondary'
}
</script>
