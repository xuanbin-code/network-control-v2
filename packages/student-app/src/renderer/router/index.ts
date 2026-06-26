import { createRouter, createWebHashHistory } from 'vue-router'
import StatusView from '@/views/StatusView.vue'
import ConfigView from '@/views/ConfigView.vue'

const routes = [
  { path: '/', component: StatusView },
  { path: '/config', component: ConfigView },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
