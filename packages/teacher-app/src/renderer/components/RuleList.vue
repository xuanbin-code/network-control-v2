<template>
  <div>
    <!-- 添加行 -->
    <div class="flex items-center gap-3 px-4 py-3 border-b">
      <Input
        v-model="newDomain"
        placeholder="输入域名，如 example.com 或 *.example.com"
        class="w-[400px]"
        @keyup.enter="add"
      />
      <Button size="sm" :disabled="store.loading || !newDomain.trim()" @click="add">
        <Plus class="size-3.5 mr-1" />
        添加
      </Button>
    </div>

    <!-- 规则表格 -->
    <Table>
      <TableHeader>
        <TableRow class="hover:bg-transparent">
          <TableHead class="w-[60px]">ID</TableHead>
          <TableHead>域名</TableHead>
          <TableHead class="w-[100px]">启用</TableHead>
          <TableHead class="w-[100px]">操作</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow v-for="row in rules" :key="row.id" class="group">
          <TableCell class="text-xs text-muted-foreground">{{ row.id }}</TableCell>
          <TableCell>
            <code class="text-sm">{{ row.domain }}</code>
          </TableCell>
          <TableCell>
            <Switch :checked="!!row.enabled" @update:checked="toggle(row)" />
          </TableCell>
          <TableCell>
            <Button size="sm" variant="ghost" class="text-muted-foreground hover:text-destructive" @click="remove(row)">
              <Trash2 class="size-3.5" />
            </Button>
          </TableCell>
        </TableRow>
        <!-- 空状态 -->
        <TableEmpty v-if="rules.length === 0" :colspan="4">
          <div class="flex flex-col items-center gap-2 py-12 text-muted-foreground">
            <FileText class="size-8" />
            <p class="text-sm">暂无规则</p>
            <p class="text-xs">在上方输入域名并点击添加</p>
          </div>
        </TableEmpty>
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
  TableEmpty,
} from '@/components/ui/table'
import { Plus, Trash2, FileText } from '@lucide/vue'

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
