import { defineStore } from 'pinia'
import { reactive, ref, watch } from 'vue'
import { settingsApi, ApiError } from '../api'

export const useSettingsStore = defineStore('settings', () => {
  const loading = ref(false)
  const error = ref(null)
  const initialized = ref(false)
  const teamMembers = ref([])
  const integrationStatus = ref({
    jira_connected: false,
    slack_connected: false,
    jira_project: null,
    slack_workspace: null,
  })

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

  // Debounce timer for auto-save
  let saveTimeout = null

  async function loadSettings() {
    loading.value = true
    error.value = null

    try {
      const data = await settingsApi.getSettings()

      // Update reminders
      if (data.reminders) {
        reminders.enabled = data.reminders.enabled
        reminders.frequency = data.reminders.frequency
        reminders.day = data.reminders.day
        reminders.time = data.reminders.time
      }

      // Update notifications
      if (data.notifications) {
        notifications.onCreate = data.notifications.on_create
        notifications.overdueWarnings = data.notifications.overdue_warnings
      }

      // Update defaults
      if (data.defaults) {
        defaults.project = data.defaults.project
        defaults.issueType = data.defaults.issue_type
      }

      initialized.value = true
    } catch (err) {
      console.error('Failed to load settings:', err)
      error.value = err instanceof ApiError ? err.message : 'Failed to load settings'
    } finally {
      loading.value = false
    }
  }

  async function saveSettings() {
    if (!initialized.value) return

    try {
      await settingsApi.updateSettings({
        reminders: {
          enabled: reminders.enabled,
          frequency: reminders.frequency,
          day: reminders.day,
          time: reminders.time,
        },
        notifications: {
          on_create: notifications.onCreate,
          overdue_warnings: notifications.overdueWarnings,
        },
        defaults: {
          project: defaults.project,
          issue_type: defaults.issueType,
        },
      })
    } catch (err) {
      console.error('Failed to save settings:', err)
      error.value = err instanceof ApiError ? err.message : 'Failed to save settings'
    }
  }

  // Auto-save settings when they change (debounced)
  function scheduleSave() {
    if (!initialized.value) return
    if (saveTimeout) {
      clearTimeout(saveTimeout)
    }
    saveTimeout = setTimeout(saveSettings, 500)
  }

  // Watch for changes and auto-save
  watch(reminders, scheduleSave, { deep: true })
  watch(notifications, scheduleSave, { deep: true })
  watch(defaults, scheduleSave, { deep: true })

  async function loadTeamMembers() {
    try {
      teamMembers.value = await settingsApi.getTeamMembers()
    } catch (err) {
      console.error('Failed to load team members:', err)
    }
  }

  async function addTeamMember(member) {
    try {
      const newMember = await settingsApi.addTeamMember(member)
      teamMembers.value.push(newMember)
      return newMember
    } catch (err) {
      console.error('Failed to add team member:', err)
      throw err
    }
  }

  async function updateTeamMember(id, updates) {
    try {
      const updated = await settingsApi.updateTeamMember(id, updates)
      const index = teamMembers.value.findIndex(m => m.id === id)
      if (index !== -1) {
        teamMembers.value[index] = updated
      }
      return updated
    } catch (err) {
      console.error('Failed to update team member:', err)
      throw err
    }
  }

  async function deleteTeamMember(id) {
    try {
      await settingsApi.deleteTeamMember(id)
      teamMembers.value = teamMembers.value.filter(m => m.id !== id)
    } catch (err) {
      console.error('Failed to delete team member:', err)
      throw err
    }
  }

  async function loadIntegrationStatus() {
    try {
      integrationStatus.value = await settingsApi.getIntegrationStatus()
    } catch (err) {
      console.error('Failed to load integration status:', err)
    }
  }

  return {
    loading,
    error,
    initialized,
    reminders,
    notifications,
    defaults,
    teamMembers,
    integrationStatus,
    loadSettings,
    saveSettings,
    loadTeamMembers,
    addTeamMember,
    updateTeamMember,
    deleteTeamMember,
    loadIntegrationStatus,
  }
})
