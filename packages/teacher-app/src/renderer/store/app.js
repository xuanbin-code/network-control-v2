import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const machines = ref([])
  const whitelist = ref([])
  const blacklist = ref([])
  const settings = ref({})
  const loading = ref(false)

  return {
    machines,
    whitelist,
    blacklist,
    settings,
    loading,
  }
})
