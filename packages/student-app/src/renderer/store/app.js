import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const status = ref({ mode: 'disconnect', connected: false, controller_url: '' })
  const config = ref({})

  return { status, config }
})
