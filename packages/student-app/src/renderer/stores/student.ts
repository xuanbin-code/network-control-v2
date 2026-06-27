import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getStatus, getConfig, updateConfig, applyMode, reloadConfig } from '@/api/student'

export const useStudentStore = defineStore('student', () => {
  const status = ref<Record<string, any>>({})
  const config = ref<Record<string, any>>({})

  async function fetchStatus() {
    status.value = await getStatus()
  }

  async function fetchConfig() {
    config.value = await getConfig()
  }

  async function saveConfig(data: Record<string, any>) {
    await updateConfig(data)
    await fetchConfig()
  }

  async function setMode(mode: string) {
    await applyMode(mode)
    await fetchStatus()
  }

  async function refreshConfig() {
    const data = await reloadConfig()
    config.value = data.config || {}
    return data
  }

  return {
    status, config,
    fetchStatus, fetchConfig, saveConfig, setMode, refreshConfig,
  }
})
