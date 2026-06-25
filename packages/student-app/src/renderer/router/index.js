import { createRouter, createWebHashHistory } from 'vue-router'
import ConfigView from '../views/ConfigView.vue'
import LockView from '../views/LockView.vue'

const routes = [
  {
    path: '/',
    name: 'config',
    component: ConfigView,
  },
  {
    path: '/lock',
    name: 'lock',
    component: LockView,
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
