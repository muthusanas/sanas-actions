<script setup>
import { useSettingsStore } from '../stores/settings'

defineProps({
  open: { type: Boolean, default: false },
})

const emit = defineEmits(['update:open'])

const settings = useSettingsStore()

function close() {
  emit('update:open', false)
}
</script>

<template>
  <!-- Overlay -->
  <div
    class="fixed inset-0 bg-black/30 z-[150] transition-opacity duration-300"
    :class="open ? 'opacity-100' : 'opacity-0 pointer-events-none'"
    @click="close"
  />

  <!-- Panel -->
  <div
    class="fixed top-0 w-[400px] h-screen bg-white border-l border-gray-200 z-[200] transition-[right] duration-300 flex flex-col shadow-lg"
    :style="{ right: open ? '0' : '-400px' }"
  >
    <div class="flex items-center justify-between px-6 py-5 border-b border-gray-200">
      <div class="text-base font-semibold">Settings</div>
      <button
        class="bg-transparent border-none text-gray-400 text-2xl cursor-pointer p-1 leading-none hover:text-gray-900"
        @click="close"
      >
        ×
      </button>
    </div>

    <div class="flex-1 p-6 overflow-y-auto">
      <!-- Reminders Section -->
      <div class="mb-8">
        <div class="text-xs uppercase tracking-wide text-gray-400 mb-4 font-semibold">Reminders</div>
        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <span class="text-sm">Enable weekly reminders</span>
          <div
            class="w-11 h-6 rounded-full relative cursor-pointer transition-all duration-150 border"
            :class="settings.reminders.enabled
              ? 'bg-accent border-accent'
              : 'bg-gray-100 border-gray-200'"
            @click="settings.reminders.enabled = !settings.reminders.enabled"
          >
            <div
              class="w-[18px] h-[18px] bg-white rounded-full absolute top-[2px] transition-all duration-150 shadow-sm"
              :style="{ left: settings.reminders.enabled ? '22px' : '2px' }"
            />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4 mt-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Frequency</label>
            <select class="select" v-model="settings.reminders.frequency">
              <option>Weekly</option>
              <option>Bi-weekly</option>
              <option>Daily</option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Day</label>
            <select class="select" v-model="settings.reminders.day">
              <option>Monday</option>
              <option>Tuesday</option>
              <option>Wednesday</option>
              <option>Thursday</option>
              <option>Friday</option>
            </select>
          </div>
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Time</label>
            <select class="select" v-model="settings.reminders.time">
              <option>9:00 AM</option>
              <option>10:00 AM</option>
              <option>2:00 PM</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Notifications Section -->
      <div class="mb-8">
        <div class="text-xs uppercase tracking-wide text-gray-400 mb-4 font-semibold">Notifications</div>
        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <span class="text-sm">Notify on ticket creation</span>
          <div
            class="w-11 h-6 rounded-full relative cursor-pointer transition-all duration-150 border"
            :class="settings.notifications.onCreate
              ? 'bg-accent border-accent'
              : 'bg-gray-100 border-gray-200'"
            @click="settings.notifications.onCreate = !settings.notifications.onCreate"
          >
            <div
              class="w-[18px] h-[18px] bg-white rounded-full absolute top-[2px] transition-all duration-150 shadow-sm"
              :style="{ left: settings.notifications.onCreate ? '22px' : '2px' }"
            />
          </div>
        </div>
        <div class="flex items-center justify-between py-3 border-b border-gray-200">
          <span class="text-sm">Include overdue warnings</span>
          <div
            class="w-11 h-6 rounded-full relative cursor-pointer transition-all duration-150 border"
            :class="settings.notifications.overdueWarnings
              ? 'bg-accent border-accent'
              : 'bg-gray-100 border-gray-200'"
            @click="settings.notifications.overdueWarnings = !settings.notifications.overdueWarnings"
          >
            <div
              class="w-[18px] h-[18px] bg-white rounded-full absolute top-[2px] transition-all duration-150 shadow-sm"
              :style="{ left: settings.notifications.overdueWarnings ? '22px' : '2px' }"
            />
          </div>
        </div>
      </div>

      <!-- Defaults Section -->
      <div class="mb-8">
        <div class="text-xs uppercase tracking-wide text-gray-400 mb-4 font-semibold">Defaults</div>
        <div class="flex flex-col gap-1.5 mb-3">
          <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Default Jira Project</label>
          <select class="select w-full" v-model="settings.defaults.project">
            <option>SANAS</option>
            <option>INFRA</option>
            <option>PLATFORM</option>
          </select>
        </div>
        <div class="flex flex-col gap-1.5">
          <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Default Issue Type</label>
          <select class="select w-full" v-model="settings.defaults.issueType">
            <option>Task</option>
            <option>Story</option>
            <option>Bug</option>
          </select>
        </div>
      </div>

      <!-- Team Mapping Section -->
      <div class="mb-8">
        <div class="text-xs uppercase tracking-wide text-gray-400 mb-4 font-semibold">Team Mapping</div>
        <p class="text-[13px] text-gray-400 mb-3">
          Map team member names to their Slack and Jira accounts.
        </p>
        <button class="btn btn-secondary w-full">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="9" cy="7" r="4" />
            <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
            <path d="M16 3.13a4 4 0 0 1 0 7.75" />
          </svg>
          Manage Team Mapping
        </button>
      </div>
    </div>
  </div>
</template>
