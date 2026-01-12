import { defineStore } from 'pinia'
import { reactive } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const reminders = reactive({
    enabled: true,
    frequency: 'Weekly',
    day: 'Monday',
    time: '9:00 AM',
  })

  const notifications = reactive({
    onCreate: true,
    overdueWarnings: true,
  })

  const defaults = reactive({
    project: 'SANAS',
    issueType: 'Task',
  })

  return {
    reminders,
    notifications,
    defaults,
  }
})
