<script setup>
import { ref, computed, onMounted } from 'vue'
import { useNotificationStore } from '../stores/notifications'
import { getInitials } from '../utils'
import { analyticsApi, notificationsApi, ApiError } from '../api'

const notificationStore = useNotificationStore()
const loading = ref(true)
const sendingReminders = ref(false)
const error = ref(null)

const stats = ref({
  completed_this_week: 0,
  pending_actions: 0,
  overdue_count: 0,
  active_team_members: 0,
})
const pendingActions = ref([])
const leaderboard = ref([])
const weeklyTrend = ref([])

const selectedActionIds = ref(new Set())

const assignableActions = computed(() => pendingActions.value.filter(a => a.assignee))
const selectedAssignableCount = computed(() =>
  assignableActions.value.filter(a => selectedActionIds.value.has(a.id)).length
)
const allAssignableSelected = computed(() =>
  assignableActions.value.length > 0 && selectedAssignableCount.value === assignableActions.value.length
)

async function loadAnalytics() {
  loading.value = true
  error.value = null

  try {
    const data = await analyticsApi.getAnalytics()
    stats.value = data.stats
    pendingActions.value = data.pending_items || []
    leaderboard.value = data.leaderboard || []
    weeklyTrend.value = data.weekly_trend || []
  } catch (err) {
    console.error('Failed to load analytics:', err)
    error.value = err instanceof ApiError ? err.message : 'Failed to load analytics'
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)

function toggleAction(id) {
  if (selectedActionIds.value.has(id)) {
    selectedActionIds.value.delete(id)
  } else {
    selectedActionIds.value.add(id)
  }
  selectedActionIds.value = new Set(selectedActionIds.value)
}

function toggleAll() {
  if (allAssignableSelected.value) {
    selectedActionIds.value = new Set()
  } else {
    selectedActionIds.value = new Set(assignableActions.value.map(a => a.id))
  }
}

async function sendReminders() {
  const selectedActions = pendingActions.value.filter(a => selectedActionIds.value.has(a.id) && a.assignee)
  const uniqueAssignees = [...new Set(selectedActions.map(a => a.assignee))]

  if (uniqueAssignees.length === 0) {
    notificationStore.show('No assignees selected')
    return
  }

  sendingReminders.value = true

  try {
    await notificationsApi.sendReminders(uniqueAssignees)
    notificationStore.show(`Reminders sent to ${uniqueAssignees.length} team member(s)`)
    selectedActionIds.value = new Set()
  } catch (err) {
    console.error('Failed to send reminders:', err)
    notificationStore.show('Failed to send reminders', '!')
  } finally {
    sendingReminders.value = false
  }
}

function getMaxCompleted() {
  return Math.max(...weeklyTrend.value.map(d => d.completed), 1)
}
</script>

<template>
  <div class="max-w-[1200px] mx-auto">
    <h1 class="text-[28px] font-semibold tracking-tight mb-2 text-gray-900">
      Analytics
    </h1>
    <p class="text-gray-600 text-[15px] mb-8">
      Track action item completion and team performance
    </p>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto"></div>
      <p class="text-gray-500 mt-2">Loading analytics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="text-center py-12">
      <p class="text-error mb-4">{{ error }}</p>
      <button class="btn btn-primary" @click="loadAnalytics">Retry</button>
    </div>

    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
            </div>
            <span class="text-sm text-gray-500">Completed This Week</span>
          </div>
          <div class="text-3xl font-semibold text-gray-900">{{ stats.completed_this_week }}</div>
          <div class="text-sm text-accent mt-1">This week</div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-warning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
            </div>
            <span class="text-sm text-gray-500">Pending Actions</span>
          </div>
          <div class="text-3xl font-semibold text-gray-900">{{ stats.pending_actions }}</div>
          <div class="text-sm text-warning mt-1">{{ stats.overdue_count }} overdue</div>
        </div>

        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <svg class="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
            </div>
            <span class="text-sm text-gray-500">Active Team Members</span>
          </div>
          <div class="text-3xl font-semibold text-gray-900">{{ stats.active_team_members }}</div>
          <div class="text-sm text-gray-400 mt-1">With assignments</div>
        </div>
      </div>

      <!-- Pending Actions with Reminder -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-lg font-semibold text-gray-900">Pending Action Items</h2>
            <p class="text-sm text-gray-400 mt-1">{{ pendingActions.length }} items pending, {{ stats.overdue_count }} overdue</p>
          </div>
          <button
            class="btn btn-primary flex items-center gap-2"
            :disabled="sendingReminders || selectedAssignableCount === 0"
            @click="sendReminders"
          >
            <svg v-if="!sendingReminders" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0" />
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25" />
              <path d="M12 2a10 10 0 0 1 10 10" />
            </svg>
            {{ sendingReminders ? 'Sending...' : selectedAssignableCount > 0 ? `Send Reminders (${selectedAssignableCount})` : 'Send Reminders' }}
          </button>
        </div>

        <!-- Select All Toggle -->
        <div v-if="pendingActions.length > 0" class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
          <div
            class="w-5 h-5 rounded border-2 flex items-center justify-center cursor-pointer transition-all duration-150 flex-shrink-0"
            :class="allAssignableSelected
              ? 'bg-accent border-accent'
              : 'border-gray-300 hover:border-gray-400'"
            @click="toggleAll"
          >
            <svg
              v-if="allAssignableSelected"
              class="w-3 h-3 text-white"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="3"
            >
              <polyline points="20 6 9 17 4 12" />
            </svg>
          </div>
          <span class="text-sm text-gray-600">
            {{ allAssignableSelected ? 'Deselect all' : 'Select all' }}
          </span>
        </div>

        <div class="space-y-3">
          <div
            v-for="action in pendingActions"
            :key="action.id"
            class="flex items-center gap-4 p-3 rounded-lg cursor-pointer"
            :class="action.overdue ? 'bg-error/5 border border-error/20' : 'bg-gray-50'"
            @click="action.assignee && toggleAction(action.id)"
          >
            <!-- Checkbox -->
            <div
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-150 flex-shrink-0"
              :class="!action.assignee
                ? 'border-gray-200 bg-gray-100 cursor-not-allowed'
                : selectedActionIds.has(action.id)
                  ? 'bg-accent border-accent cursor-pointer'
                  : 'border-gray-300 hover:border-gray-400 cursor-pointer'"
            >
              <svg
                v-if="selectedActionIds.has(action.id) && action.assignee"
                class="w-3 h-3 text-white"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="3"
              >
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
              :class="action.assignee ? 'bg-accent-light text-accent' : 'bg-gray-200 text-gray-400'"
            >
              {{ action.assignee ? getInitials(action.assignee) : '?' }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium text-gray-900 truncate">{{ action.title }}</div>
              <div class="text-xs text-gray-400">
                {{ action.assignee || 'Unassigned' }}
              </div>
            </div>
            <div class="text-xs font-medium" :class="action.overdue ? 'text-error' : 'text-gray-400'">
              {{ action.overdue ? 'Overdue' : action.due_date || '-' }}
            </div>
          </div>

          <div v-if="pendingActions.length === 0" class="text-center py-8 text-gray-400">
            No pending action items
          </div>
        </div>
      </div>

      <!-- Chart -->
      <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Weekly Completion Trend</h2>
        <div class="h-64 flex items-end justify-between gap-4 px-4">
          <div
            v-for="(day, index) in weeklyTrend"
            :key="index"
            class="flex-1 flex flex-col items-center gap-2"
          >
            <div
              class="w-full rounded-t transition-all"
              :class="index === weeklyTrend.length - 2 ? 'bg-accent' : 'bg-accent/20'"
              :style="{ height: `${(day.completed / getMaxCompleted()) * 100}%` }"
            ></div>
            <span class="text-xs text-gray-400">{{ day.week }}</span>
          </div>
        </div>
      </div>

      <!-- Team Leaderboard -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Team Leaderboard</h2>
        <div class="space-y-4">
          <div v-for="(member, index) in leaderboard" :key="member.name" class="flex items-center gap-4">
            <span class="text-sm font-medium text-gray-400 w-6">{{ index + 1 }}</span>
            <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
              {{ member.initials }}
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{{ member.name }}</div>
              <div class="text-xs text-gray-400">{{ member.completed }} completed this week</div>
            </div>
            <div class="text-sm font-semibold" :class="member.completion_percentage >= 80 ? 'text-accent' : 'text-warning'">
              {{ member.completion_percentage }}%
            </div>
          </div>

          <div v-if="leaderboard.length === 0" class="text-center py-4 text-gray-400">
            No team members with activity yet
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
