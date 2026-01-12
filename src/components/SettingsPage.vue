<script setup>
import { onMounted, ref } from 'vue'
import { useSettingsStore } from '../stores/settings'
import { getInitials } from '../utils'

const settings = useSettingsStore()

const showAddMemberModal = ref(false)
const newMember = ref({
  name: '',
  slack_id: '',
  jira_account_id: '',
  email: '',
})

onMounted(async () => {
  await Promise.all([
    settings.loadSettings(),
    settings.loadTeamMembers(),
    settings.loadIntegrationStatus(),
  ])
})

function openAddMemberModal() {
  newMember.value = { name: '', slack_id: '', jira_account_id: '', email: '' }
  showAddMemberModal.value = true
}

async function handleAddMember() {
  if (!newMember.value.name.trim()) return

  try {
    await settings.addTeamMember(newMember.value)
    showAddMemberModal.value = false
  } catch (err) {
    console.error('Failed to add member:', err)
  }
}

async function handleDeleteMember(id) {
  if (!confirm('Are you sure you want to delete this team member?')) return

  try {
    await settings.deleteTeamMember(id)
  } catch (err) {
    console.error('Failed to delete member:', err)
  }
}
</script>

<template>
  <div class="max-w-[800px] mx-auto">
    <h1 class="text-[28px] font-semibold tracking-tight mb-2 text-gray-900">
      Settings
    </h1>
    <p class="text-gray-600 text-[15px] mb-8">
      Configure your preferences and integrations
    </p>

    <!-- Loading State -->
    <div v-if="settings.loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto"></div>
      <p class="text-gray-500 mt-2">Loading settings...</p>
    </div>

    <div v-else class="space-y-6">
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
          <div
            v-for="member in settings.teamMembers"
            :key="member.id"
            class="flex items-center gap-4 p-3 bg-gray-50 rounded-lg group"
          >
            <div class="w-8 h-8 rounded-full bg-accent-light flex items-center justify-center text-xs font-semibold text-accent">
              {{ member.initials || getInitials(member.name) }}
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{{ member.name }}</div>
            </div>
            <div class="text-xs text-gray-400">{{ member.slack_id || '-' }}</div>
            <div class="text-xs text-gray-400">{{ member.jira_account_id || '-' }}</div>
            <button
              class="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-error transition-opacity"
              @click="handleDeleteMember(member.id)"
            >
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
              </svg>
            </button>
          </div>

          <div v-if="settings.teamMembers.length === 0" class="text-center py-4 text-gray-400 text-sm">
            No team members added yet
          </div>
        </div>

        <button class="btn btn-secondary mt-4" @click="openAddMemberModal">
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
                <div class="text-xs" :class="settings.integrationStatus.jira_connected ? 'text-accent' : 'text-gray-400'">
                  {{ settings.integrationStatus.jira_connected ? 'Connected' : 'Not connected' }}
                </div>
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
                <div class="text-xs" :class="settings.integrationStatus.slack_connected ? 'text-accent' : 'text-gray-400'">
                  {{ settings.integrationStatus.slack_connected ? 'Connected' : 'Not connected' }}
                </div>
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

    <!-- Add Team Member Modal -->
    <div v-if="showAddMemberModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Add Team Member</h3>

        <div class="space-y-4">
          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Name *</label>
            <input
              type="text"
              v-model="newMember.name"
              class="input"
              placeholder="John Smith"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Slack ID</label>
            <input
              type="text"
              v-model="newMember.slack_id"
              class="input"
              placeholder="@john.smith"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Jira Account ID</label>
            <input
              type="text"
              v-model="newMember.jira_account_id"
              class="input"
              placeholder="JIRA-123"
            />
          </div>

          <div class="flex flex-col gap-1.5">
            <label class="text-xs text-gray-400 uppercase tracking-wide font-medium">Email</label>
            <input
              type="email"
              v-model="newMember.email"
              class="input"
              placeholder="john.smith@example.com"
            />
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button class="btn btn-secondary flex-1" @click="showAddMemberModal = false">
            Cancel
          </button>
          <button
            class="btn btn-primary flex-1"
            :disabled="!newMember.name.trim()"
            @click="handleAddMember"
          >
            Add Member
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
