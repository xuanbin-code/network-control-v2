<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">系统设置</h2>

    <div class="max-w-[600px] space-y-4">
      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="filter_mode">过滤模式</Label>
        <Select v-model="form.filter_mode" @update:model-value="save('filter_mode')">
          <SelectTrigger id="filter_mode" class="w-[200px]">
            <SelectValue placeholder="选择过滤模式" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="whitelist">白名单</SelectItem>
            <SelectItem value="blacklist">黑名单</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="upstream_dns">上游 DNS</Label>
        <Input id="upstream_dns" v-model="form.upstream_dns" @blur="save('upstream_dns')" />
      </div>

      <div class="grid grid-cols-[160px_1fr] items-start gap-4">
        <Label for="lan_subnets">局域网网段</Label>
        <Textarea
          id="lan_subnets"
          v-model="lanSubnetsText"
          :rows="2"
          placeholder="每行一个网段，如 192.168.1.0/24"
          @blur="saveLanSubnets"
        />
      </div>

      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="tray_password_hash">托盘退出密码</Label>
        <Input id="tray_password_hash" v-model="form.tray_password_hash" @blur="save('tray_password_hash')" />
      </div>

      <div class="grid grid-cols-[160px_1fr] items-center gap-4">
        <Label for="unlock_password_hash">锁屏解锁密码</Label>
        <Input id="unlock_password_hash" v-model="form.unlock_password_hash" @blur="save('unlock_password_hash')" />
      </div>
    </div>

    <Alert class="max-w-[600px]">
      <AlertTitle>提示</AlertTitle>
      <AlertDescription>
        修改设置后会自动重新下发规则到所有在线学生端。
      </AlertDescription>
    </Alert>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const store = useTeacherStore()
const form = reactive<Record<string, any>>({})
const lanSubnetsText = ref('')

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
  await store.saveSetting(key, form[key])
}

async function saveLanSubnets() {
  const list = lanSubnetsText.value
    .split('\n')
    .map(s => s.trim())
    .filter(Boolean)
  await store.saveSetting('lan_subnets', JSON.stringify(list))
}
</script>
