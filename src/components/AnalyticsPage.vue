<script setup>
import { ref, computed } from 'vue'
import { useNotificationStore } from '../stores/notifications'
import { getInitials } from '../utils'
import { TIMING } from '../constants'

const notificationStore = useNotificationStore()
const sendingReminders = ref(false)

const pendingActions = [
  { id: 1, title: 'Review API documentation for v2 migration', assignee: 'John Smith', dueDate: 'Jan 15', overdue: false },
  { id: 2, title: 'Update deployment script for new env variables', assignee: 'Sarah Lee', dueDate: 'Jan 17', overdue: false },
  { id: 3, title: 'Schedule sync with DevOps team', assignee: 'Muthu K', dueDate: 'Jan 13', overdue: true },
  { id: 4, title: 'Create performance benchmarks', assignee: null, dueDate: 'Jan 20', overdue: false },
  { id: 5, title: 'Draft Q1 roadmap document', assignee: 'Anita Patel', dueDate: 'Jan 10', overdue: true },
  { id: 6, title: 'Fix authentication bug in mobile app', assignee: 'John Smith', dueDate: 'Jan 8', overdue: true },
  { id: 7, title: 'Review PR for caching implementation', assignee: 'Sarah Lee', dueDate: 'Jan 18', overdue: false },
  { id: 8, title: 'Update team wiki documentation', assignee: 'Muthu K', dueDate: 'Jan 19', overdue: false },
]

const selectedActionIds = ref(new Set())

const assignableActions = computed(() => pendingActions.filter(a => a.assignee))
const selectedAssignableCount = computed(() =>
  assignableActions.value.filter(a => selectedActionIds.value.has(a.id)).length
)
const allAssignableSelected = computed(() =>
  assignableActions.value.length > 0 && selectedAssignableCount.value === assignableActions.value.length
)

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

function sendReminders() {
  const selectedActions = pendingActions.filter(a => selectedActionIds.value.has(a.id) && a.assignee)
  const uniqueAssignees = [...new Set(selectedActions.map(a => a.assignee))]

  if (uniqueAssignees.length === 0) {
    notificationStore.show('No assignees selected')
    return
  }

  sendingReminders.value = true

  uniqueAssignees.forEach((assignee, i) => {
    setTimeout(() => {
      notificationStore.show(`Reminder sent to ${assignee}`)
      if (i === uniqueAssignees.length - 1) {
        sendingReminders.value = false
        selectedActionIds.value = new Set()
      }
    }, i * TIMING.NOTIFICATION_STAGGER_DELAY)
  })
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
        <div class="text-3xl font-semibold text-gray-900">24</div>
        <div class="text-sm text-accent mt-1">+12% from last week</div>
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
        <div class="text-3xl font-semibold text-gray-900">8</div>
        <div class="text-sm text-warning mt-1">3 overdue</div>
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
        <div class="text-3xl font-semibold text-gray-900">5</div>
        <div class="text-sm text-gray-400 mt-1">Across 3 projects</div>
      </div>
    </div>

    <!-- Pending Actions with Reminder -->
    <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h2 class="text-lg font-semibold text-gray-900">Pending Action Items</h2>
          <p class="text-sm text-gray-400 mt-1">{{ pendingActions.length }} items pending, {{ pendingActions.filter(a => a.overdue).length }} overdue</p>
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
      <div class="flex items-center gap-3 mb-4 pb-3 border-b border-gray-100">
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
            {{ action.overdue ? 'Overdue' : action.dueDate }}
          </div>
        </div>
      </div>
    </div>

    <!-- Chart Placeholder -->
    <div class="bg-white border border-gray-200 rounded-xl p-6 mb-8">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">Weekly Completion Trend</h2>
      <div class="h-64 flex items-end justify-between gap-4 px-4">
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 40%"></div>
          <span class="text-xs text-gray-400">Mon</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 65%"></div>
          <span class="text-xs text-gray-400">Tue</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 45%"></div>
          <span class="text-xs text-gray-400">Wed</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 80%"></div>
          <span class="text-xs text-gray-400">Thu</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent rounded-t" style="height: 100%"></div>
          <span class="text-xs text-gray-400">Fri</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 20%"></div>
          <span class="text-xs text-gray-400">Sat</span>
        </div>
        <div class="flex-1 flex flex-col items-center gap-2">
          <div class="w-full bg-accent/20 rounded-t" style="height: 10%"></div>
          <span class="text-xs text-gray-400">Sun</span>
        </div>
      </div>
    </div>

    <!-- Team Leaderboard -->
    <div class="bg-white border border-gray-200 rounded-xl p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-6">Team Leaderboard</h2>
      <div class="space-y-4">
        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-gray-400 w-6">1</span>
          <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
            SL
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900">Sarah Lee</div>
            <div class="text-xs text-gray-400">12 completed this week</div>
          </div>
          <div class="text-sm font-semibold text-accent">96%</div>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-gray-400 w-6">2</span>
          <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
            JS
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900">John Smith</div>
            <div class="text-xs text-gray-400">8 completed this week</div>
          </div>
          <div class="text-sm font-semibold text-accent">88%</div>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-gray-400 w-6">3</span>
          <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
            MK
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900">Muthu K</div>
            <div class="text-xs text-gray-400">6 completed this week</div>
          </div>
          <div class="text-sm font-semibold text-accent">82%</div>
        </div>

        <div class="flex items-center gap-4">
          <span class="text-sm font-medium text-gray-400 w-6">4</span>
          <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
            AP
          </div>
          <div class="flex-1">
            <div class="text-sm font-medium text-gray-900">Anita Patel</div>
            <div class="text-xs text-gray-400">4 completed this week</div>
          </div>
          <div class="text-sm font-semibold text-warning">67%</div>
        </div>
      </div>
    </div>
  </div>
</template>
