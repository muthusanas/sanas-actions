<script setup>
import { computed } from 'vue'
import { useActionsStore } from '../stores/actions'
import StepCard from './StepCard.vue'
import MeetingInput from './MeetingInput.vue'
import ActionItem from './ActionItem.vue'
import SuccessState from './SuccessState.vue'

const store = useActionsStore()

const selectedCount = computed(() => store.actions.filter(a => a.selected).length)
const totalCount = computed(() => store.actions.length)
const allSelected = computed(() => totalCount.value > 0 && selectedCount.value === totalCount.value)
const someSelected = computed(() => selectedCount.value > 0 && selectedCount.value < totalCount.value)
const uniqueAssignees = computed(() => new Set(store.actions.filter(a => a.selected && a.assignee).map(a => a.assignee)).size)
const unmatchedCount = computed(() => store.actions.filter(a => a.selected && !a.assignee).length)

function handleExtract(input) {
  store.extractActions(input)
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Step 1: Input Meeting Notes -->
    <StepCard
      :step="1"
      title="Add meeting notes"
      :active="store.currentStep === 1"
      :completed="store.currentStep > 1"
    >
      <MeetingInput
        v-model="store.meetingText"
        :disabled="store.currentStep > 1"
        @extract="handleExtract"
      />
    </StepCard>

    <!-- Step 2: Review Actions -->
    <StepCard
      v-if="store.currentStep >= 2"
      :step="2"
      title="Review extracted action items"
      :active="store.currentStep === 2"
      :completed="store.currentStep > 2"
    >
      <template #badge>
        <span class="badge badge-info">AI Extracted</span>
      </template>

      <!-- Loading State -->
      <div v-if="store.loading" class="flex items-center justify-center py-12 text-gray-400">
        <div class="spinner"></div>
        <span>Analyzing meeting notes with Claude...</span>
      </div>

      <!-- Error State -->
      <div v-else-if="store.error" class="py-8 text-center">
        <div class="text-error mb-2">{{ store.error }}</div>
        <button class="btn btn-secondary" @click="store.reset">Try Again</button>
      </div>

      <!-- Action Items -->
      <template v-else>
        <div :class="{ 'opacity-60 pointer-events-none': store.currentStep > 2 }">
          <!-- Select All Header -->
          <div class="flex items-center gap-3 pb-3 mb-3 border-b border-gray-200">
            <div
              class="w-5 h-5 border-2 rounded flex items-center justify-center transition-all duration-150 flex-shrink-0"
              :class="[
                allSelected
                  ? 'bg-accent border-accent text-white'
                  : someSelected
                    ? 'bg-accent/50 border-accent text-white'
                    : 'bg-white border-gray-300 hover:border-accent',
                store.currentStep > 2 ? 'cursor-not-allowed' : 'cursor-pointer'
              ]"
              @click="store.currentStep <= 2 && store.toggleAllActions()"
            >
              <svg v-if="allSelected" class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <svg v-else-if="someSelected" class="w-2 h-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4">
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </div>
            <span class="text-sm text-gray-600">
              <template v-if="allSelected">Deselect all</template>
              <template v-else>Select all ({{ totalCount }})</template>
            </span>
          </div>

          <div class="flex flex-col gap-3">
            <ActionItem
              v-for="(action, index) in store.actions"
              :key="action.id"
              :action="action"
              :disabled="store.currentStep > 2"
              @toggle="store.toggleAction(index)"
              @remove="store.removeAction(index)"
              @update="store.updateAction(index, $event)"
            />
          </div>

          <!-- Config Row -->
          <div class="flex gap-4 mt-5 pt-5 border-t border-gray-200">
            <div class="flex flex-col gap-1.5">
              <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Jira Project</label>
              <select class="select" v-model="store.config.project" :disabled="store.currentStep > 2">
                <option>SANAS</option>
                <option>INFRA</option>
                <option>PLATFORM</option>
              </select>
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Issue Type</label>
              <select class="select" v-model="store.config.issueType" :disabled="store.currentStep > 2">
                <option>Task</option>
                <option>Story</option>
                <option>Bug</option>
              </select>
            </div>
            <div class="flex flex-col gap-1.5">
              <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Labels</label>
              <select class="select" v-model="store.config.label" :disabled="store.currentStep > 2">
                <option>meeting-action</option>
                <option>sprint-planning</option>
                <option>follow-up</option>
              </select>
            </div>
          </div>
        </div>
      </template>

      <!-- Summary Footer -->
      <template #footer v-if="!store.loading">
        <div
          class="flex items-center justify-end gap-6 px-6 py-5 bg-gray-50 border-t border-gray-200"
          :class="{ 'opacity-60': store.currentStep > 2 }"
        >
          <span v-if="unmatchedCount > 0" class="badge badge-warning">
            {{ unmatchedCount }} unmatched
          </span>
          <div class="flex items-center gap-2">
            <span class="text-xl font-semibold text-gray-900">{{ selectedCount }}</span>
            <span class="text-[13px] text-gray-400">selected</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xl font-semibold text-gray-900">{{ uniqueAssignees }}</span>
            <span class="text-[13px] text-gray-400">assignees</span>
          </div>
          <button
            class="btn btn-primary"
            :disabled="store.currentStep > 2"
            @click="store.createTickets"
          >
            <svg v-if="store.currentStep <= 2" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            {{ store.currentStep > 2 ? 'Tickets Created' : 'Create Tickets & Notify' }}
          </button>
        </div>
      </template>
    </StepCard>

    <!-- Step 3: Success -->
    <StepCard
      v-if="store.currentStep === 3"
      :step="3"
      title="Tickets created successfully"
      :active="true"
      :completed="false"
      success
    >
      <SuccessState
        :tickets="store.createdTickets"
        @reset="store.reset"
      />
    </StepCard>
  </div>
</template>
