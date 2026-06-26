import { createRouter, createWebHashHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import RulesView from '@/views/RulesView.vue'
import SettingsView from '@/views/SettingsView.vue'

const routes = [
  { path: '/', component: DashboardView },
  { path: '/rules', component: RulesView },
  { path: '/settings', component: SettingsView },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
