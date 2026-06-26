<template>
  <div class="settings-page">
    <h2>系统设置</h2>

    <el-form label-width="160px" style="max-width: 600px;">
      <el-form-item label="过滤模式">
        <el-select v-model="form.filter_mode" @change="save('filter_mode')">
          <el-option label="白名单" value="whitelist" />
          <el-option label="黑名单" value="blacklist" />
        </el-select>
      </el-form-item>

      <el-form-item label="上游 DNS">
        <el-input v-model="form.upstream_dns" @blur="save('upstream_dns')" />
      </el-form-item>

      <el-form-item label="局域网网段">
        <el-input
          v-model="lanSubnetsText"
          type="textarea"
          :rows="2"
          placeholder="每行一个网段，如 192.168.1.0/24"
          @blur="saveLanSubnets"
        />
      </el-form-item>

      <el-form-item label="托盘退出密码">
        <el-input v-model="form.tray_password_hash" @blur="save('tray_password_hash')" />
      </el-form-item>

      <el-form-item label="锁屏解锁密码">
        <el-input v-model="form.unlock_password_hash" @blur="save('unlock_password_hash')" />
      </el-form-item>
    </el-form>

    <el-alert type="info" :closable="false" style="margin-top: 20px;">
      修改设置后会自动重新下发规则到所有在线学生端。
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { useTeacherStore } from '@/stores/teacher'

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

<style scoped>
.settings-page {
  padding: 20px;
}
</style>
