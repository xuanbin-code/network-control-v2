<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold tracking-tight">规则管理</h2>

    <Tabs v-model="activeTab" default-value="whitelist">
      <TabsList>
        <TabsTrigger value="whitelist">白名单</TabsTrigger>
        <TabsTrigger value="blacklist">黑名单</TabsTrigger>
      </TabsList>
      <TabsContent value="whitelist">
        <RuleList list-type="whitelist" :rules="store.rules.whitelist" />
      </TabsContent>
      <TabsContent value="blacklist">
        <RuleList list-type="blacklist" :rules="store.rules.blacklist" />
      </TabsContent>
    </Tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import RuleList from '@/components/RuleList.vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const store = useTeacherStore()
const activeTab = ref('whitelist')

onMounted(() => {
  store.fetchRules()
})
</script>
