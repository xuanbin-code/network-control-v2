import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getMachines, getRules, getSettings, scanNetwork,
  setNetwork, enableNetwork, disableNetwork, enableIp, disableIp,
  addRule, deleteRule, toggleRule, updateSetting,
} from '@/api/teacher'

export const useTeacherStore = defineStore('teacher', () => {
  const machines = ref<any[]>([])
  const rules = ref({ whitelist: [], blacklist: [] })
  const settings = ref<Record<string, any>>({})
  const loading = ref(false)

  async function fetchMachines() {
    machines.value = await getMachines()
  }

  async function fetchRules() {
    rules.value = await getRules()
  }

  async function fetchSettings() {
    settings.value = await getSettings()
  }

  async function setMode(mode: string, targets?: string[]) {
    loading.value = true
    await setNetwork(mode, targets)
    loading.value = false
    await fetchMachines()
  }

  async function enableAll() {
    await enableNetwork()
    await fetchMachines()
  }

  async function disableAll() {
    await disableNetwork()
    await fetchMachines()
  }

  async function enableSingle(ip: string) {
    await enableIp(ip)
    await fetchMachines()
  }

  async function disableSingle(ip: string) {
    await disableIp(ip)
    await fetchMachines()
  }

  async function createRule(listType: string, domain: string) {
    await addRule(listType, domain)
    await fetchRules()
  }

  async function removeRule(listType: string, ruleId: number) {
    await deleteRule(listType, ruleId)
    await fetchRules()
  }

  async function switchRule(listType: string, ruleId: number) {
    await toggleRule(listType, ruleId)
    await fetchRules()
  }

  async function saveSetting(key: string, value: string) {
    await updateSetting(key, value)
    await fetchSettings()
  }

  async function scanSubnet(subnet: string) {
    return scanNetwork(subnet)
  }

  return {
    machines, rules, settings, loading,
    fetchMachines, fetchRules, fetchSettings,
    setMode, enableAll, disableAll, enableSingle, disableSingle,
    createRule, removeRule, switchRule, saveSetting, scanSubnet,
  }
})
