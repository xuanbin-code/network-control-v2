<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">配置</h2>

    <div class="max-w-[600px] space-y-4">
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="controller_url">教师端 WebSocket</Label>
        <Input id="controller_url" v-model="form.controller_url" />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="controller_api_url">教师端 HTTP API</Label>
        <Input id="controller_api_url" v-model="form.controller_api_url" />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="upstream_dns">上游 DNS</Label>
        <Input id="upstream_dns" v-model="form.upstream_dns" />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-start gap-4">
        <Label for="lan_subnets">局域网网段</Label>
        <Textarea
          id="lan_subnets"
          v-model="lanSubnetsText"
          :rows="2"
          placeholder="每行一个网段"
        />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="tray_password_hash">托盘退出密码</Label>
        <Input id="tray_password_hash" v-model="form.tray_password_hash" />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="unlock_password_hash">锁屏解锁密码</Label>
        <Input id="unlock_password_hash" v-model="form.unlock_password_hash" />
      </div>
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <div />
        <div class="flex items-center gap-3">
          <Button :disabled="saving" @click="save">
            {{ saving ? '保存中...' : '保存配置' }}
          </Button>
          <Button variant="outline" :disabled="reloading" @click="reload">
            {{ reloading ? '加载中...' : '重新加载配置' }}
          </Button>
          <span v-if="reloadMsg" class="text-sm text-green-600">{{ reloadMsg }}</span>
        </div>
      </div>
    </div>

    <Alert class="max-w-[600px]">
      <AlertTitle>注意</AlertTitle>
      <AlertDescription>
        修改配置需要管理员权限才能写入 config.json，保存后建议重启服务生效。
      </AlertDescription>
    </Alert>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useStudentStore } from '@/stores/student'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

const store = useStudentStore()
const form = reactive<Record<string, any>>({})
const lanSubnetsText = ref('')
const saving = ref(false)
const reloading = ref(false)
const reloadMsg = ref('')

onMounted(async () => {
  await store.fetchConfig()
  Object.assign(form, store.config)
  if (Array.isArray(form.lan_subnets)) {
    lanSubnetsText.value = form.lan_subnets.join('\n')
  }
})

async function reload() {
  reloading.value = true
  reloadMsg.value = ''
  try {
    await store.refreshConfig()
    Object.assign(form, store.config)
    if (Array.isArray(form.lan_subnets)) {
      lanSubnetsText.value = form.lan_subnets.join('\n')
    }
    reloadMsg.value = '已重新加载'
  } catch (e) {
    reloadMsg.value = '加载失败'
  } finally {
    reloading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    form.lan_subnets = lanSubnetsText.value
      .split('\n')
      .map(s => s.trim())
      .filter(Boolean)
    await store.saveConfig({ ...form })
  } finally {
    saving.value = false
  }
}
</script>
