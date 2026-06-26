<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">控制面板</h2>

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
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

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
