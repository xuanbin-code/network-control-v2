<template>
  <div class="config-page">
    <h2>配置</h2>

    <el-form label-width="160px" style="max-width: 600px;">
      <el-form-item label="教师端 WebSocket">
        <el-input v-model="form.controller_url" />
      </el-form-item>
      <el-form-item label="教师端 HTTP API">
        <el-input v-model="form.controller_api_url" />
      </el-form-item>
      <el-form-item label="上游 DNS">
        <el-input v-model="form.upstream_dns" />
      </el-form-item>
      <el-form-item label="局域网网段">
        <el-input
          v-model="lanSubnetsText"
          type="textarea"
          :rows="2"
          placeholder="每行一个网段"
        />
      </el-form-item>
      <el-form-item label="托盘退出密码">
        <el-input v-model="form.tray_password_hash" />
      </el-form-item>
      <el-form-item label="锁屏解锁密码">
        <el-input v-model="form.unlock_password_hash" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="save" :loading="saving">保存配置</el-button>
      </el-form-item>
    </el-form>

    <el-alert type="warning" :closable="false" style="margin-top: 20px;">
      修改配置需要管理员权限才能写入 config.json，保存后建议重启服务生效。
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useStudentStore } from '@/stores/student'

const store = useStudentStore()
const form = reactive<Record<string, any>>({})
const lanSubnetsText = ref('')
const saving = ref(false)

onMounted(async () => {
  await store.fetchConfig()
  Object.assign(form, store.config)
  if (Array.isArray(form.lan_subnets)) {
    lanSubnetsText.value = form.lan_subnets.join('\n')
  }
})

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

<style scoped>
.config-page {
  padding: 20px;
}
</style>
