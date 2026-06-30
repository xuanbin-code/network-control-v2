<template>
  <!-- 浅色玻璃质感侧边栏 -->
  <aside class="w-[240px] flex flex-col select-none relative"
    style="background: linear-gradient(180deg, hsla(173, 25%, 97%, 0.98) 0%, hsla(173, 20%, 96%, 0.98) 100%); backdrop-filter: blur(16px) saturate(120%); -webkit-backdrop-filter: blur(16px) saturate(120%); border-right: 1px solid hsla(173, 15%, 88%, 0.7);"
  >
    <!-- 品牌区 -->
    <div class="h-14 flex items-center gap-3 px-4 border-b border-black/5 shrink-0">
      <div class="size-8 rounded-lg flex items-center justify-center shrink-0"
        style="background: linear-gradient(135deg, hsl(173, 75%, 41%) 0%, hsl(173, 60%, 32%) 100%); box-shadow: 0 2px 8px hsla(173, 75%, 41%, 0.25);">
        <GraduationCap class="size-4 text-white" />
      </div>
      <div class="min-w-0">
        <div class="text-sm font-semibold text-slate-700/90 leading-tight">网络控制</div>
        <div class="text-[10px] text-slate-400 leading-tight">教师端</div>
      </div>
    </div>

    <!-- 主导航 -->
    <nav class="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
      <RouterLink
        v-for="item in primaryItems"
        :key="item.path"
        :to="item.path"
        :style="isActive(item.path) ? activeStyle : undefined"
        class="flex items-center gap-3 px-3 py-2 rounded-lg border border-transparent text-sm font-medium transition-colors duration-200 text-slate-500 hover:text-slate-800 hover:bg-slate-100 focus:outline-none"
        :class="{ 'text-slate-800': isActive(item.path) }"
      >
        <component :is="item.icon" class="size-4 shrink-0" :stroke-width="isActive(item.path) ? 2.5 : 2" />
        <span>{{ item.label }}</span>
        <span
          v-if="item.badge !== undefined"
          class="ml-auto inline-flex items-center justify-center min-w-[20px] h-5 rounded-full px-1.5 text-[10px] font-semibold"
          :class="isActive(item.path) ? 'bg-white/25 text-white' : 'bg-slate-200 text-slate-500'"
        >
          {{ item.badge }}
        </span>
      </RouterLink>

      <!-- 预留扩展区 -->
      <template v-for="group in navGroups" :key="group.label">
        <div class="mt-6 mb-1.5 px-3">
          <p class="text-[10px] font-semibold uppercase tracking-[0.15em] text-slate-400">{{ group.label }}</p>
        </div>
        <RouterLink
          v-for="child in group.children"
          :key="child.path"
          :to="child.path"
          :style="isActive(child.path) ? activeStyle : undefined"
          class="flex items-center gap-3 px-3 py-2 rounded-lg border border-transparent text-sm font-medium transition-colors duration-200 text-slate-500 hover:text-slate-800 hover:bg-slate-100 focus:outline-none"
          :class="{ 'text-slate-800': isActive(child.path) }"
        >
          <component :is="child.icon" class="size-4 shrink-0" :stroke-width="isActive(child.path) ? 2.5 : 2" />
          <span>{{ child.label }}</span>
        </RouterLink>
      </template>
    </nav>

    <!-- 底部 -->
    <div class="h-11 flex items-center gap-2.5 px-4 border-t border-black/5 shrink-0">
      <div class="size-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white/70 shrink-0"
        style="background: linear-gradient(135deg, hsl(173, 75%, 45%) 0%, hsl(173, 55%, 35%) 100%);">
        T
      </div>
      <span class="text-xs text-slate-400">教师</span>
      <span class="ml-auto text-[10px] text-slate-300">v1.0.0</span>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { GraduationCap, Monitor, FileText, Settings } from '@lucide/vue'

interface NavItem {
  path: string
  label: string
  icon: any
  badge?: number
}

interface NavGroup {
  label: string
  children: NavItem[]
}

const route = useRoute()

const isActive = (path: string) => route.path === path

// 激活态：青绿渐变背景 + 白色文字 + 柔和阴影
const activeStyle = {
  background: 'linear-gradient(135deg, hsla(173, 75%, 41%, 0.92) 0%, hsla(173, 60%, 34%, 0.92) 100%)',
  boxShadow: '0 2px 8px hsla(173, 75%, 41%, 0.18), inset 0 1px 0 hsla(173, 75%, 55%, 0.2)',
  border: '1px solid hsla(173, 60%, 38%, 0.25)',
}

// ── 当前菜单项 ──
const primaryItems: NavItem[] = [
  { path: '/', label: '控制面板', icon: Monitor },
  { path: '/rules', label: '规则管理', icon: FileText },
  { path: '/settings', label: '系统设置', icon: Settings },
]

// ── 预留扩展分组 ──
const navGroups: NavGroup[] = []
</script>
