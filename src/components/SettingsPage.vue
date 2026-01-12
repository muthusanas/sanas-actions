<script setup>
import { useSettingsStore } from '../stores/settings'

const settings = useSettingsStore()
</script>

<template>
  <div class="max-w-[800px] mx-auto">
    <h1 class="text-[28px] font-semibold tracking-tight mb-2 text-gray-900">
      Settings
    </h1>
    <p class="text-gray-600 text-[15px] mb-8">
      Configure your preferences and integrations
    </p>

    <div class="space-y-6">
      <!-- Reminders Section -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Reminders</h2>

        <div class="flex items-center justify-between py-4 border-b border-gray-100">
          <div>
            <div class="text-sm font-medium text-gray-900">Enable weekly reminders</div>
            <div class="text-xs text-gray-400 mt-1">Get notified about pending action items</div>
          </div>
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

        <div class="grid grid-cols-3 gap-4 mt-6">
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
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Notifications</h2>

        <div class="flex items-center justify-between py-4 border-b border-gray-100">
          <div>
            <div class="text-sm font-medium text-gray-900">Notify on ticket creation</div>
            <div class="text-xs text-gray-400 mt-1">Send Slack message when tickets are created</div>
          </div>
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

        <div class="flex items-center justify-between py-4">
          <div>
            <div class="text-sm font-medium text-gray-900">Include overdue warnings</div>
            <div class="text-xs text-gray-400 mt-1">Highlight overdue items in notifications</div>
          </div>
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
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Default Values</h2>

        <div class="grid grid-cols-2 gap-4">
          <div class="flex flex-col gap-1.5">
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
      </div>

      <!-- Team Mapping Section -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-2">Team Mapping</h2>
        <p class="text-sm text-gray-400 mb-6">
          Map team member names to their Slack and Jira accounts for automatic assignment.
        </p>

        <div class="space-y-3">
          <div class="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
              JS
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">John Smith</div>
            </div>
            <div class="text-xs text-gray-400">@john.smith</div>
            <div class="text-xs text-gray-400">JIRA-123</div>
          </div>

          <div class="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
              SL
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">Sarah Lee</div>
            </div>
            <div class="text-xs text-gray-400">@sarah.lee</div>
            <div class="text-xs text-gray-400">JIRA-456</div>
          </div>

          <div class="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
            <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
              MK
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">Muthu K</div>
            </div>
            <div class="text-xs text-gray-400">@muthu.k</div>
            <div class="text-xs text-gray-400">JIRA-789</div>
          </div>
        </div>

        <button class="btn btn-secondary mt-4">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          Add Team Member
        </button>
      </div>

      <!-- Integrations Section -->
      <div class="bg-white border border-gray-200 rounded-xl p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">Integrations</h2>

        <div class="space-y-4">
          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 bg-[#0052CC] rounded-lg flex items-center justify-center">
                <span class="text-white text-xs font-bold">JIRA</span>
              </div>
              <div>
                <div class="text-sm font-medium text-gray-900">Jira</div>
                <div class="text-xs text-accent">Connected</div>
              </div>
            </div>
            <button class="btn btn-secondary text-sm py-1.5">Configure</button>
          </div>

          <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 bg-[#4A154B] rounded-lg flex items-center justify-center">
                <span class="text-white text-xs font-bold">S</span>
              </div>
              <div>
                <div class="text-sm font-medium text-gray-900">Slack</div>
                <div class="text-xs text-accent">Connected</div>
              </div>
            </div>
            <button class="btn btn-secondary text-sm py-1.5">Configure</button>
          </div>

          <div class="flex items-center justify-between p-4 border border-dashed border-gray-200 rounded-lg">
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
              </div>
              <div>
                <div class="text-sm font-medium text-gray-900">Add Integration</div>
                <div class="text-xs text-gray-400">Connect more tools</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
