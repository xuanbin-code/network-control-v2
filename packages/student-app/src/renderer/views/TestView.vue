<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">功能测试</h2>
    <p class="text-muted-foreground">
      本页面用于在本地测试学生端各项功能，仅在开发/调试时使用。
    </p>

    <Card>
      <CardHeader>
        <CardTitle>黑屏安静测试</CardTitle>
      </CardHeader>
      <CardContent class="space-y-4">
        <div class="flex items-center gap-4">
          <Label class="min-w-[80px]">倒计时</Label>
          <Input
            v-model.number="countdown"
            type="number"
            :disabled="infinite"
            class="w-32"
            placeholder="秒数"
          />
          <span class="text-sm text-muted-foreground">秒</span>
        </div>

        <div class="flex items-center gap-2">
          <input
            id="infinite"
            v-model="infinite"
            type="checkbox"
            class="size-4 rounded border-gray-300"
          />
          <Label for="infinite" class="text-sm font-normal">持续黑屏（需手动或 IPC 解除）</Label>
        </div>

        <div class="flex gap-3 pt-2">
          <Button :disabled="loading" @click="startBlackScreen">
            <Monitor class="mr-2 size-4" />
            {{ loading ? '启动中...' : '启动黑屏测试' }}
          </Button>
          <Button variant="outline" :disabled="unlockLoading" @click="sendUnlock">
            <Unlock class="mr-2 size-4" />
            {{ unlockLoading ? '解除中...' : 'IPC 解除黑屏' }}
          </Button>
        </div>

        <Alert v-if="message" :variant="messageType" class="mt-4">
          <AlertDescription>{{ message }}</AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Monitor, Unlock } from '@lucide/vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { testBlackScreen, sendBlackScreenUnlock } from '@/api/student'

const countdown = ref(30)
const infinite = ref(false)
const loading = ref(false)
const unlockLoading = ref(false)
const message = ref('')
const messageType = ref<'default' | 'destructive'>('default')

function showMessage(text: string, type: 'default' | 'destructive' = 'default') {
  message.value = text
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

async function startBlackScreen() {
  loading.value = true
  try {
    const seconds = infinite.value ? 0 : countdown.value
    const res = await testBlackScreen(seconds)
    if (res.ok) {
      showMessage(
        `黑屏测试已启动（PID: ${res.pid}，${res.infinite ? '持续黑屏' : `倒计时 ${res.countdown_seconds} 秒`}）`
      )
    } else {
      showMessage('启动失败：' + (res.error || '未知错误'), 'destructive')
    }
  } catch (err: any) {
    showMessage('请求失败：' + (err.message || String(err)), 'destructive')
  } finally {
    loading.value = false
  }
}

async function sendUnlock() {
  unlockLoading.value = true
  try {
    const ok = await sendBlackScreenUnlock()
    showMessage(ok ? '已发送 IPC 解除命令' : '未找到黑屏进程或解除失败', ok ? 'default' : 'destructive')
  } catch (err: any) {
    showMessage('请求失败：' + (err.message || String(err)), 'destructive')
  } finally {
    unlockLoading.value = false
  }
}
</script>
