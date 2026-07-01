<template>
  <div class="flex h-screen bg-background">
    <aside class="w-[180px] flex flex-col bg-[#304156] text-[#bfcbd9]">
      <div class="h-[60px] flex items-center justify-center border-b border-[#1f2d3d] text-base font-bold text-white">
        网络控制 学生端
      </div>
      <nav class="flex-1 py-4">
        <div
          v-for="group in menuGroups"
          :key="group.title"
          class="mb-2"
        >
          <div class="px-6 py-2 text-xs font-semibold text-[#909399]">
            {{ group.title }}
          </div>
          <RouterLink
            v-for="item in group.items"
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
        </div>
      </nav>
    </aside>
    <main class="flex-1 overflow-auto p-6">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { Monitor, Settings, FlaskConical } from '@lucide/vue'

const menuGroups = [
  {
    title: '常规',
    items: [
      { path: '/', label: '状态', icon: Monitor },
      { path: '/config', label: '配置', icon: Settings },
    ],
  },
  {
    title: '测试',
    items: [
      { path: '/test', label: '功能测试', icon: FlaskConical },
    ],
  },
]
</script>
