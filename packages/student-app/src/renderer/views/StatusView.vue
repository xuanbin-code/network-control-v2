<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">当前状态</h2>

    <Alert v-if="store.status.mode === 'disconnect'" variant="destructive">
      <AlertDescription>
        已断网：当前仅保留局域网与教师端连接，互联网访问已被阻断。
      </AlertDescription>
    </Alert>

    <Dialog v-model:open="dialogOpen">
      <DialogContent class="sm:max-w-md">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <Mail class="size-5" />
            教师端消息
          </DialogTitle>
          <DialogDescription class="text-base text-foreground whitespace-pre-wrap pt-2">
            {{ dialogMessage }}
          </DialogDescription>
        </DialogHeader>
        <DialogFooter showCloseButton />
      </DialogContent>
    </Dialog>

    <Card>
      <CardHeader>
        <CardTitle>运行状态</CardTitle>
      </CardHeader>
      <CardContent>
        <dl class="grid gap-3 text-sm">
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">连接状态</dt>
            <dd>
              <Badge :variant="store.status.connected ? 'default' : 'destructive'">
                {{ store.status.connected ? '已连接教师端' : '未连接' }}
              </Badge>
            </dd>
          </div>
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">当前模式</dt>
            <dd>
              <Badge :variant="modeVariant">{{ modeLabel }}</Badge>
            </dd>
          </div>
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">教师端地址</dt>
            <dd>{{ store.status.controller_url || '-' }}</dd>
          </div>
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">本机 IP</dt>
            <dd>{{ store.status.controller_ip || '-' }}</dd>
          </div>
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">主机名</dt>
            <dd>{{ store.status.hostname || '-' }}</dd>
          </div>
          <div class="flex justify-between border-b py-2">
            <dt class="text-muted-foreground">MAC</dt>
            <dd>{{ store.status.mac || '-' }}</dd>
          </div>
          <div class="flex justify-between py-2">
            <dt class="text-muted-foreground">规则数量</dt>
            <dd>{{ store.status.rule_count || 0 }}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>

    <div class="grid grid-cols-4 gap-4">
      <Button
        :variant="store.status.mode === 'normal' ? 'default' : 'outline'"
        size="lg"
        class="w-full"
        @click="store.setMode('normal')"
      >
        开网
      </Button>
      <Button
        :variant="store.status.mode === 'disconnect' ? 'destructive' : 'outline'"
        size="lg"
        class="w-full"
        @click="store.setMode('disconnect')"
      >
        断网
      </Button>
      <Button
        :variant="store.status.mode === 'whitelist' ? 'secondary' : 'outline'"
        size="lg"
        class="w-full"
        @click="store.setMode('whitelist')"
      >
        白名单
      </Button>
      <Button
        :variant="store.status.mode === 'blacklist' ? 'secondary' : 'outline'"
        size="lg"
        class="w-full"
        @click="store.setMode('blacklist')"
      >
        黑名单
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, computed, ref, watch } from 'vue'
import { Mail } from '@lucide/vue'
import { useStudentStore } from '@/stores/student'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'

const store = useStudentStore()
let timer: number | undefined

const dialogOpen = ref(false)
const dialogMessage = ref('')

onMounted(() => {
  store.fetchStatus()
  timer = window.setInterval(() => store.fetchStatus(), 3000)
})

// 最近 60 秒内收到的教师端测试消息
const recentTestMessage = computed(() => {
  const msg = store.status.last_test_message
  const ts = store.status.last_test_message_ts
  if (!msg || !ts) return ''
  const now = Date.now() / 1000
  if (now - ts > 60) return ''
  return msg
})

// 收到新消息时自动弹窗
watch(recentTestMessage, (newMsg) => {
  if (newMsg) {
    dialogMessage.value = newMsg
    dialogOpen.value = true
  }
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

const modeVariant = computed(() => {
  const map: Record<string, any> = {
    normal: 'default',
    whitelist: 'secondary',
    blacklist: 'outline',
    disconnect: 'destructive',
  }
  return map[store.status.mode] || 'secondary'
})
</script>
