<template>
  <div class="space-y-4">
    <div class="flex items-center gap-3">
      <Input
        v-model="newDomain"
        placeholder="输入域名，如 example.com 或 *.example.com"
        class="w-[360px]"
        @keyup.enter="add"
      />
      <Button :disabled="store.loading" @click="add">添加</Button>
    </div>

    <Table>
      <TableHeader>
        <TableRow>
          <TableHead class="w-[60px]">ID</TableHead>
          <TableHead>域名</TableHead>
          <TableHead class="w-[100px]">启用</TableHead>
          <TableHead class="w-[100px]">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="row in rules" :key="row.id">
          <TableCell>{{ row.id }}</TableCell>
          <TableCell>{{ row.domain }}</TableCell>
          <TableCell>
            <Switch :checked="row.enabled" @update:checked="toggle(row)" />
          </TableCell>
          <TableCell>
            <Button size="sm" variant="destructive" @click="remove(row)">删除</Button>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

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
