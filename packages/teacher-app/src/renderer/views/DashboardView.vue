<template>
  <div class="space-y-6">
    <!-- ═══ 统计卡片 ═══ -->
    <div class="grid grid-cols-4 gap-4">
      <Card v-for="stat in statsCards" :key="stat.label" class="shadow-sm">
        <CardContent class="p-4 flex items-center gap-3">
          <div :class="['size-10 rounded-lg flex items-center justify-center', stat.bg]">
            <component :is="stat.icon" :class="['size-5', stat.iconColor]" />
          </div>
          <div>
            <p class="text-2xs font-medium text-muted-foreground uppercase tracking-wider">{{ stat.label }}</p>
            <p class="text-2xl font-bold text-foreground">{{ stat.value }}</p>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- ═══ 服务器信息栏（压缩） ═══ -->
    <div class="flex items-center gap-4 px-4 py-2 rounded-lg border bg-card text-xs text-muted-foreground">
      <span>本机 <code class="text-foreground font-medium">{{ store.serverInfo.ip || '--' }}</code></span>
      <Separator orientation="vertical" class="h-3" />
      <span>WS <code class="text-foreground font-medium">{{ store.serverInfo.ws_url || '--' }}</code></span>
      <div class="ml-auto flex items-center gap-1.5">
        <span class="relative flex size-1.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
          <span class="relative inline-flex rounded-full size-1.5 bg-success" />
        </span>
        <span>每 3s 自动刷新</span>
      </div>
    </div>

    <!-- ═══ 工具栏：筛选 + 扫描 + 批量操作 ═══ -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <!-- 筛选标签 -->
      <div class="flex items-center gap-1 bg-muted rounded-lg p-0.5">
        <button
          v-for="tab in filterTabs"
          :key="tab.key"
          @click="activeFilter = tab.key"
          :class="[
            'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
            activeFilter === tab.key
              ? 'bg-background text-foreground shadow-xs'
              : 'text-muted-foreground hover:text-foreground',
          ]"
        >
          {{ tab.label }}
          <span
            v-if="tab.key !== 'all'"
            :class="[
              'ml-1.5 inline-flex items-center justify-center min-w-[18px] h-[18px] rounded-full px-1 text-2xs font-medium',
              tab.key === 'online' ? 'bg-success/10 text-success' : 'bg-muted-foreground/10 text-muted-foreground',
            ]"
          >
            {{ tab.count }}
          </span>
        </button>
      </div>

      <!-- 右侧操作 -->
      <div class="flex items-center gap-2">
        <Input v-model="scanSubnet" placeholder="192.168.1.0/24" class="w-[180px] h-8 text-sm" />
        <Button size="sm" variant="outline" @click="doScan" :disabled="scanning">
          <ScanSearch class="size-3.5 mr-1" />
          扫描
        </Button>
        <Separator orientation="vertical" class="h-5" />
        <Button size="sm" variant="default" @click="handleEnableAll" :disabled="store.loading">
          <Wifi class="size-3.5 mr-1" />
          全部开网
        </Button>
        <Button size="sm" variant="destructive" @click="handleDisableAll" :disabled="store.loading">
          <WifiOff class="size-3.5 mr-1" />
          全部断网
        </Button>
        <Button size="sm" variant="secondary" @click="handleSetWhitelist" :disabled="store.loading">
          白名单
        </Button>
        <Button size="sm" variant="outline" @click="handleSetBlacklist" :disabled="store.loading">
          黑名单
        </Button>
      </div>
    </div>

    <!-- ═══ 机器表格 ═══ -->
    <!-- 骨架屏 -->
    <template v-if="isInitialLoad">
      <div class="grid grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="rounded-lg border bg-card p-4 animate-pulse">
          <div class="flex items-center gap-3">
            <div class="size-10 rounded-lg bg-muted" />
            <div class="space-y-2">
              <div class="h-3 w-16 rounded bg-muted" />
              <div class="h-6 w-10 rounded bg-muted" />
            </div>
          </div>
        </div>
      </div>
      <Card class="shadow-sm mt-4">
        <div v-for="i in 5" :key="i" class="flex items-center gap-4 px-4 py-3 border-b last:border-0 animate-pulse">
          <div class="h-4 w-24 rounded bg-muted" />
          <div class="h-4 w-20 rounded bg-muted" />
          <div class="h-4 w-32 rounded bg-muted" />
          <div class="h-5 w-14 rounded-full bg-muted" />
          <div class="h-4 w-10 rounded bg-muted" />
          <div class="h-4 w-28 rounded bg-muted ml-auto" />
        </div>
      </Card>
    </template>

    <!-- 真实表格 -->
    <Card v-else class="shadow-sm overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow class="hover:bg-transparent">
            <TableHead class="w-[130px]">IP 地址</TableHead>
            <TableHead class="w-[140px]">主机名</TableHead>
            <TableHead class="w-[150px]">MAC 地址</TableHead>
            <TableHead class="w-[90px]">模式</TableHead>
            <TableHead class="w-[72px]">状态</TableHead>
            <TableHead class="w-[130px]">最后心跳</TableHead>
            <TableHead class="w-[40px]"><span class="sr-only">操作</span></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow v-for="row in filteredMachines" :key="row.ip" class="group">
            <!-- IP -->
            <TableCell>
              <span class="font-mono text-sm">{{ row.ip }}</span>
            </TableCell>
            <!-- 主机名 -->
            <TableCell class="text-sm max-w-[140px] truncate">
              {{ row.hostname || '-' }}
            </TableCell>
            <!-- MAC -->
            <TableCell>
              <code class="text-xs text-muted-foreground">{{ row.mac || '-' }}</code>
            </TableCell>
            <!-- 模式芯片 -->
            <TableCell>
              <span :class="modeChipClass(row.mode)" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border">
                {{ modeLabel(row.mode) }}
              </span>
            </TableCell>
            <!-- 在线状态 -->
            <TableCell>
              <div class="flex items-center gap-1.5">
                <span
                  :class="row.online ? 'bg-emerald-500' : 'bg-gray-300'"
                  class="size-2 rounded-full inline-block shrink-0"
                />
                <span class="text-sm" :class="row.online ? 'text-emerald-700 font-medium' : 'text-muted-foreground'">
                  {{ row.online ? '在线' : '离线' }}
                </span>
              </div>
            </TableCell>
            <!-- 最后心跳 -->
            <TableCell class="text-xs text-muted-foreground">
              {{ row.last_heartbeat ? formatRelativeTime(row.last_heartbeat) : '-' }}
            </TableCell>
            <!-- 操作下拉 -->
            <TableCell class="text-right">
              <DropdownMenu>
                <DropdownMenuTrigger as-child>
                  <Button variant="ghost" size="icon-sm" class="opacity-0 group-hover:opacity-100 transition-opacity">
                    <MoreHorizontal class="size-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" class="w-36">
                  <DropdownMenuItem @select="store.enableSingle(row.ip)">
                    <Wifi class="size-3.5 mr-2" />
                    开网
                  </DropdownMenuItem>
                  <DropdownMenuItem @select="store.disableSingle(row.ip)">
                    <WifiOff class="size-3.5 mr-2" />
                    断网
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem @select="store.setMode('whitelist', [row.ip])">
                    白名单模式
                  </DropdownMenuItem>
                  <DropdownMenuItem @select="store.setMode('blacklist', [row.ip])">
                    黑名单模式
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem @select="openTestDialog(row.ip)">
                    <MessageSquare class="size-3.5 mr-2" />
                    测试消息
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem @select="openBlackScreenDialog(row.ip)">
                    <MonitorOff class="size-3.5 mr-2" />
                    黑屏测试
                  </DropdownMenuItem>
                  <DropdownMenuItem @select="handleBlackScreenUnlock(row.ip)">
                    <Monitor class="size-3.5 mr-2" />
                    解除黑屏
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TableCell>
          </TableRow>
          <!-- 空状态 -->
          <TableEmpty v-if="filteredMachines.length === 0" :colspan="7">
            <div class="flex flex-col items-center gap-2 py-12 text-muted-foreground">
              <MonitorOff class="size-8" />
              <p class="text-sm">暂无机器数据</p>
              <Button variant="outline" size="sm" @click="store.fetchMachines">
                <RotateCw class="size-3.5 mr-1" />
                刷新列表
              </Button>
            </div>
          </TableEmpty>
        </TableBody>
      </Table>
    </Card>

    <!-- ═══ 扫描结果对话框 ═══ -->
    <Dialog v-model:open="scanVisible">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>扫描结果</DialogTitle>
          <DialogDescription>网段 {{ scanSubnet }} 中发现 {{ scanResults.length }} 台机器</DialogDescription>
        </DialogHeader>
        <div class="flex flex-wrap gap-2 py-2">
          <Badge v-for="ip in scanResults" :key="ip" variant="secondary">{{ ip }}</Badge>
        </div>
      </DialogContent>
    </Dialog>

    <!-- ═══ 测试消息对话框 ═══ -->
    <Dialog v-model:open="testVisible">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>发送测试消息</DialogTitle>
          <DialogDescription v-if="testTargetIp">目标: {{ testTargetIp }}</DialogDescription>
          <DialogDescription v-else>目标: 全部在线学生端</DialogDescription>
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
            <Button :disabled="!testMessage.trim() || sending" @click="doSendTest">
              <Loader2 v-if="sending" class="size-3.5 mr-1 animate-spin" />
              {{ sending ? '发送中...' : '发送' }}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>

    <!-- ═══ 黑屏测试对话框 ═══ -->
    <Dialog v-model:open="blackScreenVisible">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>黑屏安静测试</DialogTitle>
          <DialogDescription>目标: {{ blackScreenTargetIp || '全部在线学生端' }}</DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div>
            <Label for="black-screen-countdown">倒计时秒数</Label>
            <Input
              id="black-screen-countdown"
              v-model.number="blackScreenCountdown"
              type="number"
              min="0"
              placeholder="30"
              class="mt-2"
            />
            <p class="text-xs text-muted-foreground mt-1.5">
              0 表示持续黑屏，需通过「解除黑屏」手动关闭。
            </p>
          </div>
          <DialogFooter>
            <Button variant="outline" @click="blackScreenVisible = false">取消</Button>
            <Button
              :disabled="blackScreenLoading || !Number.isFinite(blackScreenCountdown) || blackScreenCountdown < 0"
              @click="doSendBlackScreen"
              variant="destructive"
            >
              <Loader2 v-if="blackScreenLoading" class="size-3.5 mr-1 animate-spin" />
              {{ blackScreenLoading ? '发送中...' : '启动黑屏' }}
            </Button>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { toast } from 'vue-sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { Card, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableEmpty,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Monitor,
  Wifi,
  WifiOff,
  ScanSearch,
  MoreHorizontal,
  MessageSquare,
  MonitorOff,
  RotateCw,
  Loader2,
  HardDrive,
  Shield,
  Filter,
} from '@lucide/vue'
import { formatRelativeTime } from '@/lib/time'

const store = useTeacherStore()

// ── 筛选 ──
const activeFilter = ref('all')
const filterTabs = computed(() => {
  const machines = store.machines
  return [
    { key: 'all', label: '全部', count: machines.length },
    { key: 'online', label: '在线', count: machines.filter((m: any) => m.online).length },
    { key: 'offline', label: '离线', count: machines.filter((m: any) => !m.online).length },
  ]
})

const filteredMachines = computed(() => {
  const machines = store.machines
  if (activeFilter.value === 'online') return machines.filter((m: any) => m.online)
  if (activeFilter.value === 'offline') return machines.filter((m: any) => !m.online)
  return machines
})

const isInitialLoad = ref(true)

// ── 统计卡片 ──
const onlineCount = computed(() => store.machines.filter((m: any) => m.online).length)
const totalCount = computed(() => store.machines.length)
const activeRulesCount = computed(() => {
  const wl = (store.rules as any).whitelist || []
  const bl = (store.rules as any).blacklist || []
  return wl.filter((r: any) => r.enabled).length + bl.filter((r: any) => r.enabled).length
})
const currentFilterMode = computed(() => {
  const mode = (store.settings as any).filter_mode || ''
  const map: Record<string, string> = { whitelist: '白名单', blacklist: '黑名单', normal: '正常' }
  return map[mode] || mode || '--'
})

const statsCards = computed(() => [
  { label: '在线机器', value: onlineCount.value, icon: Monitor, bg: 'bg-primary/10', iconColor: 'text-primary' },
  { label: '总机器数', value: totalCount.value, icon: HardDrive, bg: 'bg-success/10', iconColor: 'text-success' },
  { label: '活跃规则', value: activeRulesCount.value, icon: Shield, bg: 'bg-warning/10', iconColor: 'text-warning' },
  { label: '过滤模式', value: currentFilterMode.value, icon: Filter, bg: 'bg-accent', iconColor: 'text-accent-foreground' },
])

// ── 扫描 ──
const scanSubnet = ref('192.168.1.0/24')
const scanning = ref(false)
const scanVisible = ref(false)
const scanResults = ref<string[]>([])

// ── 测试消息 ──
const testVisible = ref(false)
const testTargetIp = ref('')
const testMessage = ref('')
const sending = ref(false)

// ── 黑屏测试 ──
const blackScreenVisible = ref(false)
const blackScreenTargetIp = ref('')
const blackScreenCountdown = ref(30)
const blackScreenLoading = ref(false)

// ── 轮询 ──
let timer: number | undefined

onMounted(async () => {
  store.fetchServerInfo()
  store.fetchRules()
  store.fetchSettings()
  await store.fetchMachines()
  isInitialLoad.value = false
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
    toast.success(`发现 ${res.ips.length} 台在线机器`)
  } catch {
    toast.error('网段扫描失败，请检查网络连接')
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
    const res = await store.testMessage(testMessage.value.trim(), targets)
    testVisible.value = false

    const delivery = res?.data?.delivery
    if (delivery) {
      const { total, delivered, not_connected } = delivery
      if (delivered === total && total > 0) {
        toast.success(`测试消息已发送到 ${delivered} 个学生端`)
      } else if (delivered > 0) {
        toast.warning(`测试消息已发送到 ${delivered}/${total} 个学生端，${not_connected} 个离线`)
      } else if (total === 0) {
        toast.info('没有在线的学生端，测试消息未发送')
      } else {
        toast.error(`测试消息下发失败：所有 ${total} 个目标学生端均不在线`)
      }
    } else {
      toast.success('测试消息已发送')
    }
  } catch {
    toast.error('发送失败，请稍后重试')
  } finally {
    sending.value = false
  }
}

function openBlackScreenDialog(ip: string) {
  blackScreenTargetIp.value = ip
  blackScreenCountdown.value = 30
  blackScreenVisible.value = true
}

async function doSendBlackScreen() {
  // 规范化倒计时：空值或非数字时回退到 30 秒
  let countdown = Number(blackScreenCountdown.value)
  if (!Number.isFinite(countdown) || countdown < 0) {
    countdown = 30
  }
  countdown = Math.floor(countdown)

  blackScreenLoading.value = true
  try {
    const targets = blackScreenTargetIp.value ? [blackScreenTargetIp.value] : undefined
    const res = await store.blackScreen(countdown, targets)
    blackScreenVisible.value = false

    const delivery = res?.data?.delivery
    if (delivery) {
      const { total, delivered, not_connected, failed } = delivery
      if (delivered === total && total > 0) {
        toast.success(`黑屏指令已下发到 ${delivered} 个学生端`)
      } else if (delivered > 0) {
        const parts: string[] = [`已下发到 ${delivered}/${total} 个学生端`]
        if (not_connected > 0) parts.push(`${not_connected} 个离线`)
        if (failed > 0) parts.push(`${failed} 个发送失败`)
        toast.warning(`黑屏指令部分送达：${parts.join('，')}`)
      } else if (total === 0) {
        toast.info('没有在线的学生端，黑屏指令未发送')
      } else {
        toast.error(`黑屏指令下发失败：所有 ${total} 个目标学生端均不在线`)
      }
    } else {
      toast.success('黑屏指令已下发')
    }
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '黑屏指令下发失败'
    toast.error(msg)
  } finally {
    blackScreenLoading.value = false
  }
}

async function handleBlackScreenUnlock(ip: string) {
  try {
    const res = await store.blackScreenUnlock([ip])
    const delivery = res?.data?.delivery
    if (delivery && delivery.delivered === 0) {
      toast.error('解除黑屏指令下发失败：学生端不在线')
    } else {
      toast.success('解除黑屏指令已下发')
    }
  } catch {
    toast.error('解除黑屏指令下发失败')
  }
}

async function handleEnableAll() {
  try {
    await store.enableAll()
    toast.success('已下发全部开网指令')
  } catch {
    toast.error('操作失败')
  }
}

async function handleDisableAll() {
  try {
    await store.disableAll()
    toast.success('已下发全部断网指令')
  } catch {
    toast.error('操作失败')
  }
}

async function handleSetWhitelist() {
  try {
    await store.setMode('whitelist')
    toast.success('已切换为白名单模式')
  } catch {
    toast.error('操作失败')
  }
}

async function handleSetBlacklist() {
  try {
    await store.setMode('blacklist')
    toast.success('已切换为黑名单模式')
  } catch {
    toast.error('操作失败')
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

function modeChipClass(mode: string) {
  const map: Record<string, string> = {
    normal: 'bg-sky-50 text-sky-700 border-sky-200',
    whitelist: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    blacklist: 'bg-amber-50 text-amber-700 border-amber-200',
    disconnect: 'bg-rose-50 text-rose-700 border-rose-200',
  }
  return map[mode] || 'bg-gray-50 text-gray-600 border-gray-200'
}
</script>
