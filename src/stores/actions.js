import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { useNotificationStore } from './notifications'
import { TIMING } from '../constants'
import { getUniqueValues } from '../utils'
import { actionsApi, notificationsApi, ApiError } from '../api'

export const useActionsStore = defineStore('actions', () => {
  const currentStep = ref(1)
  const loading = ref(false)
  const error = ref(null)
  const meetingText = ref('')
  const uploadedFile = ref(null)
  const inputType = ref(null) // 'text' or 'file'

  const actions = ref([])
  const createdTickets = ref([])
  const pendingTimeouts = ref([])

  const config = reactive({
    project: 'SANAS',
    issueType: 'Task',
    label: 'meeting-action',
  })

  async function extractActions(input) {
    if (!input) return

    const { type, content, file } = input

    // Validate input based on type
    if (type === 'text' && !content?.trim()) return
    if (type === 'file' && !file) return

    inputType.value = type
    if (type === 'text') {
      meetingText.value = content
    } else {
      uploadedFile.value = file
    }

    currentStep.value = 2
    loading.value = true
    error.value = null

    try {
      let response
      if (type === 'text') {
        response = await actionsApi.extractFromText(content)
      } else {
        response = await actionsApi.extractFromFile(file)
      }

      // Map backend response to frontend format
      actions.value = response.action_items.map(item => ({
        id: item.id,
        title: item.title,
        assignee: item.assignee,
        dueDate: item.due_date,
        selected: item.selected,
        overdue: item.overdue,
      }))
    } catch (err) {
      console.error('Failed to extract actions:', err)
      error.value = err instanceof ApiError ? err.message : 'Failed to extract action items'
      // Go back to step 1 on error
      currentStep.value = 1
    } finally {
      loading.value = false
    }
  }

  function toggleAction(index) {
    actions.value[index].selected = !actions.value[index].selected
  }

  function toggleAllActions() {
    const allSelected = actions.value.every(a => a.selected)
    const newState = !allSelected
    actions.value.forEach(a => a.selected = newState)
  }

  function removeAction(index) {
    actions.value.splice(index, 1)
  }

  function updateAction(index, updates) {
    actions.value[index] = { ...actions.value[index], ...updates }
  }

  async function createTickets() {
    const selectedActions = actions.value.filter(a => a.selected)
    if (selectedActions.length === 0) return

    loading.value = true
    error.value = null

    try {
      const actionIds = selectedActions.map(a => a.id)
      const response = await actionsApi.createTickets(actionIds, config)

      createdTickets.value = response.tickets.map(ticket => ({
        key: ticket.key,
        assignee: ticket.assignee,
        url: ticket.url,
      }))

      currentStep.value = 3

      // Send notifications to assignees
      scheduleAssigneeNotifications(selectedActions)
    } catch (err) {
      console.error('Failed to create tickets:', err)
      error.value = err instanceof ApiError ? err.message : 'Failed to create tickets'
    } finally {
      loading.value = false
    }
  }

  function scheduleAssigneeNotifications(selectedActions) {
    const notificationStore = useNotificationStore()
    const assignees = getUniqueValues(selectedActions, 'assignee')

    assignees.forEach((assignee, i) => {
      const timeoutId = setTimeout(async () => {
        try {
          // Find ticket key for this assignee
          const ticket = createdTickets.value.find(t => t.assignee === assignee)
          await notificationsApi.sendNotification(
            assignee,
            `You have been assigned a new action item`,
            ticket?.key
          )
          notificationStore.show(`Slack notification sent to ${assignee}`)
        } catch (err) {
          console.error(`Failed to notify ${assignee}:`, err)
          notificationStore.show(`Failed to notify ${assignee}`, '!')
        }
      }, i * TIMING.NOTIFICATION_STAGGER_DELAY)
      pendingTimeouts.value.push(timeoutId)
    })
  }

  function reset() {
    // Clear pending notification timeouts to prevent memory leaks
    pendingTimeouts.value.forEach(id => clearTimeout(id))
    pendingTimeouts.value = []

    currentStep.value = 1
    loading.value = false
    error.value = null
    meetingText.value = ''
    uploadedFile.value = null
    inputType.value = null
    actions.value = []
    createdTickets.value = []
  }

  return {
    currentStep,
    loading,
    error,
    meetingText,
    uploadedFile,
    inputType,
    actions,
    config,
    createdTickets,
    extractActions,
    toggleAction,
    toggleAllActions,
    removeAction,
    updateAction,
    createTickets,
    reset,
  }
})
