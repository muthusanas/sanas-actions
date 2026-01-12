<script setup>
import { TEAM_MEMBERS } from '../constants'
import { getInitials } from '../utils'

const props = defineProps({
  action: { type: Object, required: true },
})

const emit = defineEmits(['toggle', 'remove', 'assign'])

function handleAssignClick() {
  if (!props.action.assignee) {
    // For demo, assign a random team member
    const randomIndex = Math.floor(Math.random() * TEAM_MEMBERS.length)
    emit('assign', TEAM_MEMBERS[randomIndex].name)
  }
}
</script>

<template>
  <div
    class="grid items-center gap-4 p-4 bg-gray-50 border border-gray-200 rounded-lg transition-all duration-150 hover:border-gray-300 hover:shadow-sm"
    :class="{ 'border-warning bg-warning-light': !action.assignee }"
    style="grid-template-columns: auto 1fr auto auto auto;"
  >
    <!-- Checkbox -->
    <div
      class="w-5 h-5 border-2 rounded cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 bg-white"
      :class="action.selected
        ? 'bg-accent border-accent'
        : 'border-gray-300 hover:border-accent'"
      @click="emit('toggle')"
    >
      <span v-if="action.selected" class="text-white text-xs font-bold">✓</span>
    </div>

    <!-- Title -->
    <div class="text-sm text-gray-900">{{ action.title }}</div>

    <!-- Assignee -->
    <div
      class="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-[13px] text-gray-600 min-w-[140px]"
      :class="{ 'border-warning text-warning cursor-pointer bg-warning/10': !action.assignee }"
      @click="handleAssignClick"
    >
      <template v-if="action.assignee">
        <div class="w-5 h-5 rounded-full bg-accent-light flex items-center justify-center text-[10px] font-semibold text-accent">
          {{ getInitials(action.assignee) }}
        </div>
        {{ action.assignee }}
      </template>
      <template v-else>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        Select assignee
      </template>
    </div>

    <!-- Due Date -->
    <div
      class="text-[13px] text-gray-400 font-mono min-w-[80px] text-right"
      :class="{ 'text-error font-medium': action.overdue }"
    >
      {{ action.dueDate }}
    </div>

    <!-- Remove Button -->
    <button
      class="w-7 h-7 rounded flex items-center justify-center text-gray-400 hover:bg-error/10 hover:text-error transition-all duration-150"
      @click="emit('remove')"
    >
      ×
    </button>
  </div>
</template>
