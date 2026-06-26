<template>
  <div class="rules-page">
    <h2>规则管理</h2>

    <el-tabs v-model="activeTab" type="border-card">
      <el-tab-pane label="白名单" name="whitelist">
        <rule-list list-type="whitelist" :rules="store.rules.whitelist" />
      </el-tab-pane>
      <el-tab-pane label="黑名单" name="blacklist">
        <rule-list list-type="blacklist" :rules="store.rules.blacklist" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTeacherStore } from '@/stores/teacher'
import RuleList from '@/components/RuleList.vue'

const store = useTeacherStore()
const activeTab = ref('whitelist')

onMounted(() => {
  store.fetchRules()
})
</script>

<style scoped>
.rules-page {
  padding: 20px;
}
</style>
