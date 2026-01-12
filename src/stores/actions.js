import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { useNotificationStore } from './notifications'
import { TIMING, TICKET } from '../constants'
import { getUniqueValues } from '../utils'

export const useActionsStore = defineStore('actions', () => {
  const currentStep = ref(1)
  const loading = ref(false)
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

  // Sample data that would come from AI extraction
  const sampleActions = [
    { id: 1, title: 'Review and finalize API documentation for v2 migration', assignee: 'John Smith', dueDate: 'Jan 15', selected: true, overdue: false },
    { id: 2, title: 'Update deployment script to handle new environment variables', assignee: 'Sarah Lee', dueDate: 'Jan 17', selected: true, overdue: false },
    { id: 3, title: 'Schedule sync with DevOps to discuss CI/CD improvements', assignee: 'Muthu K', dueDate: 'Jan 13', selected: true, overdue: false },
    { id: 4, title: 'Create performance benchmarks for the new caching layer', assignee: null, dueDate: 'Jan 20', selected: true, overdue: false },
    { id: 5, title: 'Draft Q1 roadmap document and share with stakeholders', assignee: 'Anita Patel', dueDate: 'Jan 10', selected: true, overdue: true },
  ]

  function extractActions(input) {
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

    // Simulate API call to AI extraction service
    // In production, this would send text or file to backend for processing
    setTimeout(() => {
      actions.value = sampleActions.map(a => ({ ...a }))
      loading.value = false
    }, TIMING.API_SIMULATION_DELAY)
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

  function createTickets() {
    const selectedActions = actions.value.filter(a => a.selected)

    createdTickets.value = selectedActions.map((action, i) => ({
      key: `${config.project}-${TICKET.STARTING_NUMBER + i}`,
      assignee: action.assignee,
    }))

    currentStep.value = 3
    scheduleAssigneeNotifications(selectedActions)
  }

  function scheduleAssigneeNotifications(selectedActions) {
    const notificationStore = useNotificationStore()
    const assignees = getUniqueValues(selectedActions, 'assignee')

    assignees.forEach((assignee, i) => {
      const timeoutId = setTimeout(() => {
        notificationStore.show(`Slack notification sent to ${assignee}`)
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
    meetingText.value = ''
    uploadedFile.value = null
    inputType.value = null
    actions.value = []
    createdTickets.value = []
  }

  return {
    currentStep,
    loading,
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
