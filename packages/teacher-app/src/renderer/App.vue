<template>
  <div class="flex h-screen bg-background">
    <aside class="w-[200px] flex flex-col bg-[#304156] text-[#bfcbd9]">
      <div class="h-[60px] flex items-center justify-center border-b border-[#1f2d3d] text-lg font-bold text-white">
        网络控制 教师端
      </div>
      <nav class="flex-1 py-4">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-6 py-3 text-sm transition-colors hover:text-white',
            $route.path === item.path ? 'text-[#409EFF] bg-[#263445]' : 'text-[#bfcbd9]',
          ]"
        >
          <component :is="item.icon" class="size-4" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>
    <main class="flex-1 overflow-auto p-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { Monitor, FileText, Settings } from '@lucide/vue'

const menuItems = [
  { path: '/', label: '控制面板', icon: Monitor },
  { path: '/rules', label: '规则管理', icon: FileText },
  { path: '/settings', label: '系统设置', icon: Settings },
]
</script>
