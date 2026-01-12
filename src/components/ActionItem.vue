<script setup>
import { ref } from 'vue'
import { TEAM_MEMBERS } from '../constants'
import { getInitials } from '../utils'

const props = defineProps({
  action: { type: Object, required: true },
})

const emit = defineEmits(['toggle', 'remove', 'update'])

const editingTitle = ref(false)
const editingAssignee = ref(false)
const editingDueDate = ref(false)
const titleInput = ref(null)
const dueDateInput = ref(null)

function startEditingTitle() {
  editingTitle.value = true
  setTimeout(() => titleInput.value?.focus(), 0)
}

function saveTitle(event) {
  const newTitle = event.target.value.trim()
  if (newTitle && newTitle !== props.action.title) {
    emit('update', { title: newTitle })
  }
  editingTitle.value = false
}

function handleTitleKeydown(event) {
  if (event.key === 'Enter') {
    saveTitle(event)
  } else if (event.key === 'Escape') {
    editingTitle.value = false
  }
}

function selectAssignee(name) {
  emit('update', { assignee: name })
  editingAssignee.value = false
}

function clearAssignee() {
  emit('update', { assignee: null })
  editingAssignee.value = false
}

function startEditingDueDate() {
  editingDueDate.value = true
  setTimeout(() => dueDateInput.value?.focus(), 0)
}

function saveDueDate(event) {
  const newDate = event.target.value
  if (newDate) {
    // Format date as "Mon DD" (e.g., "Jan 15")
    const date = new Date(newDate)
    const formatted = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    emit('update', { dueDate: formatted })
  }
  editingDueDate.value = false
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

    <!-- Title (Editable) -->
    <div class="min-w-0">
      <input
        v-if="editingTitle"
        ref="titleInput"
        type="text"
        :value="action.title"
        class="w-full text-sm text-gray-900 bg-white border border-accent rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-accent/20"
        @blur="saveTitle"
        @keydown="handleTitleKeydown"
      />
      <div
        v-else
        class="text-sm text-gray-900 cursor-text hover:bg-white hover:px-2 hover:py-1 hover:-mx-2 hover:-my-1 hover:rounded transition-all truncate"
        @click="startEditingTitle"
        :title="action.title"
      >
        {{ action.title }}
      </div>
    </div>

    <!-- Assignee (Editable Dropdown) -->
    <div class="relative">
      <div
        class="flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-[13px] text-gray-600 min-w-[140px] cursor-pointer hover:border-gray-300 transition-all"
        :class="{ 'border-warning text-warning bg-warning/10': !action.assignee }"
        @click="editingAssignee = !editingAssignee"
      >
        <template v-if="action.assignee">
          <div class="w-5 h-5 rounded-full bg-accent-light flex items-center justify-center text-[10px] font-semibold text-accent">
            {{ getInitials(action.assignee) }}
          </div>
          <span class="truncate">{{ action.assignee }}</span>
        </template>
        <template v-else>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          Select assignee
        </template>
        <svg class="w-3 h-3 ml-auto text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      <!-- Assignee Dropdown -->
      <div
        v-if="editingAssignee"
        class="absolute top-full left-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10 py-1"
      >
        <button
          v-for="member in TEAM_MEMBERS"
          :key="member.name"
          class="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 flex items-center gap-2 transition-colors"
          :class="{ 'bg-accent/5 text-accent': action.assignee === member.name }"
          @click="selectAssignee(member.name)"
        >
          <div class="w-6 h-6 rounded-full bg-accent-light flex items-center justify-center text-[10px] font-semibold text-accent">
            {{ member.initials }}
          </div>
          {{ member.name }}
        </button>
        <button
          v-if="action.assignee"
          class="w-full px-3 py-2 text-left text-sm text-gray-400 hover:bg-gray-50 border-t border-gray-100 transition-colors"
          @click="clearAssignee"
        >
          Clear assignee
        </button>
      </div>

      <!-- Click outside to close -->
      <div
        v-if="editingAssignee"
        class="fixed inset-0 z-0"
        @click="editingAssignee = false"
      />
    </div>

    <!-- Due Date (Editable) -->
    <div class="relative">
      <input
        v-if="editingDueDate"
        ref="dueDateInput"
        type="date"
        class="text-[13px] font-mono bg-white border border-accent rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-accent/20"
        @blur="saveDueDate"
        @change="saveDueDate"
      />
      <div
        v-else
        class="text-[13px] text-gray-400 font-mono min-w-[80px] text-right cursor-pointer hover:text-gray-600 transition-colors"
        :class="{ 'text-error font-medium': action.overdue }"
        @click="startEditingDueDate"
      >
        {{ action.dueDate }}
      </div>
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
