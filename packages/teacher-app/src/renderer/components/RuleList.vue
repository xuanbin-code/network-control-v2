<template>
  <div>
    <el-input
      v-model="newDomain"
      placeholder="输入域名，如 example.com 或 *.example.com"
      style="width: 360px; margin-right: 10px;"
      @keyup.enter="add"
    />
    <el-button type="primary" @click="add" :loading="store.loading">添加</el-button>

    <el-table :data="rules" style="width: 100%; margin-top: 16px;" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="domain" label="域名" />
      <el-table-column prop="enabled" label="启用" width="80">
        <template #default="{ row }">
          <el-switch v-model="row.enabled" @change="toggle(row)" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'

const props = defineProps<{
  listType: string
  rules: any[]
}>()

const store = useTeacherStore()
const newDomain = ref('')

async function add() {
  if (!newDomain.value.trim()) return
  await store.createRule(props.listType, newDomain.value.trim())
  newDomain.value = ''
}

async function remove(row: any) {
  await store.removeRule(props.listType, row.id)
}

async function toggle(row: any) {
  await store.switchRule(props.listType, row.id)
}
</script>
