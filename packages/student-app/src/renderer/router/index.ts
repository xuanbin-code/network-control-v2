import { createRouter, createWebHashHistory } from 'vue-router'
import StatusView from '@/views/StatusView.vue'
import ConfigView from '@/views/ConfigView.vue'
import TestView from '@/views/TestView.vue'

const routes = [
  { path: '/', component: StatusView },
  { path: '/config', component: ConfigView },
  { path: '/test', component: TestView },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
