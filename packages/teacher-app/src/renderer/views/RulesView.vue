<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-page-title">规则管理</h2>
      <div class="flex items-center gap-2">
        <Button variant="outline" size="sm" disabled>
          <Upload class="size-3.5 mr-1" />
          导入
        </Button>
        <Button variant="outline" size="sm" disabled>
          <Download class="size-3.5 mr-1" />
          导出
        </Button>
      </div>
    </div>

    <Tabs v-model="activeTab" default-value="whitelist">
      <TabsList>
        <TabsTrigger value="whitelist" class="gap-2">
          白名单
          <span class="inline-flex items-center justify-center min-w-[20px] h-5 rounded-full bg-muted px-1.5 text-2xs font-medium text-muted-foreground">
            {{ store.rules.whitelist.length }}
          </span>
        </TabsTrigger>
        <TabsTrigger value="blacklist" class="gap-2">
          黑名单
          <span class="inline-flex items-center justify-center min-w-[20px] h-5 rounded-full bg-muted px-1.5 text-2xs font-medium text-muted-foreground">
            {{ store.rules.blacklist.length }}
          </span>
        </TabsTrigger>
      </TabsList>
      <TabsContent value="whitelist">
        <Card class="shadow-sm">
          <CardContent class="p-0">
            <RuleList list-type="whitelist" :rules="store.rules.whitelist" />
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="blacklist">
        <Card class="shadow-sm">
          <CardContent class="p-0">
            <RuleList list-type="blacklist" :rules="store.rules.blacklist" />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import RuleList from '@/components/RuleList.vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Upload, Download } from '@lucide/vue'

const store = useTeacherStore()
const activeTab = ref('whitelist')

onMounted(() => {
  store.fetchRules()
})
</script>
