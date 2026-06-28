<template>
  <div class="space-y-6">
    <h2 class="text-page-title">系统设置</h2>

    <div class="max-w-[640px] space-y-6">
      <!-- 网络配置 -->
      <Card class="shadow-sm">
        <CardHeader class="pb-3">
          <CardTitle class="text-base">网络配置</CardTitle>
          <CardDescription>控制过滤模式和 DNS 设置</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-[140px_1fr] items-center gap-4">
            <Label for="filter_mode" class="text-sm text-muted-foreground">过滤模式</Label>
            <Select v-model="form.filter_mode" @update:model-value="save('filter_mode')">
              <SelectTrigger id="filter_mode" class="w-[200px]">
                <SelectValue placeholder="选择过滤模式" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="whitelist">白名单（仅允许列表中域名）</SelectItem>
                <SelectItem value="blacklist">黑名单（禁止列表中域名）</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div class="grid grid-cols-[140px_1fr] items-center gap-4">
            <Label for="upstream_dns" class="text-sm text-muted-foreground">上游 DNS</Label>
            <Input id="upstream_dns" v-model="form.upstream_dns" @blur="save('upstream_dns')" />
          </div>

          <div class="grid grid-cols-[140px_1fr] items-start gap-4">
            <Label for="lan_subnets" class="text-sm text-muted-foreground pt-2">局域网网段</Label>
            <Textarea
              id="lan_subnets"
              v-model="lanSubnetsText"
              :rows="3"
              placeholder="每行一个网段，如 192.168.1.0/24"
              @blur="saveLanSubnets"
            />
          </div>
        </CardContent>
      </Card>

      <!-- 安全设置 -->
      <Card class="shadow-sm">
        <CardHeader class="pb-3">
          <CardTitle class="text-base">安全设置</CardTitle>
          <CardDescription>学生端密码配置</CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="grid grid-cols-[140px_1fr] items-center gap-4">
            <Label for="tray_password_hash" class="text-sm text-muted-foreground">托盘退出密码</Label>
            <Input id="tray_password_hash" v-model="form.tray_password_hash" type="password"
                   placeholder="输入新密码" @blur="save('tray_password_hash')" />
          </div>

          <div class="grid grid-cols-[140px_1fr] items-center gap-4">
            <Label for="unlock_password_hash" class="text-sm text-muted-foreground">锁屏解锁密码</Label>
            <Input id="unlock_password_hash" v-model="form.unlock_password_hash" type="password"
                   placeholder="输入新密码" @blur="save('unlock_password_hash')" />
          </div>
        </CardContent>
      </Card>

      <!-- 自动保存指示器 -->
      <div class="flex items-center gap-2 text-xs text-muted-foreground">
        <CheckCircle2 v-if="!saving" class="size-3.5 text-success" />
        <Loader2 v-else class="size-3.5 animate-spin" />
        {{ saving ? '保存中...' : '设置已自动保存' }}
      </div>

      <!-- 提示 -->
      <Alert>
        <AlertTitle>提示</AlertTitle>
        <AlertDescription>
          修改网络配置后会自动重新下发规则到所有在线学生端。
        </AlertDescription>
      </Alert>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { CheckCircle2, Loader2 } from '@lucide/vue'

const store = useTeacherStore()
const form = reactive<Record<string, any>>({})
const lanSubnetsText = ref('')
const saving = ref(false)

onMounted(async () => {
  await store.fetchSettings()
  Object.assign(form, store.settings)
  if (Array.isArray(form.lan_subnets)) {
    lanSubnetsText.value = form.lan_subnets.join('\n')
  }
})

watch(() => store.settings, (val) => {
  Object.assign(form, val)
  if (Array.isArray(form.lan_subnets)) {
    lanSubnetsText.value = form.lan_subnets.join('\n')
  }
})

async function save(key: string) {
  saving.value = true
  try {
    await store.saveSetting(key, form[key])
  } finally {
    saving.value = false
  }
}

async function saveLanSubnets() {
  const list = lanSubnetsText.value
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
  saving.value = true
  try {
    await store.saveSetting('lan_subnets', JSON.stringify(list))
  } finally {
    saving.value = false
  }
}
</script>
