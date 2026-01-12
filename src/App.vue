<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import CreateTab from './components/CreateTab.vue'
import HistoryTab from './components/HistoryTab.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import NotificationToast from './components/NotificationToast.vue'

const activeTab = ref('create')
const settingsOpen = ref(false)
</script>

<template>
  <div class="min-h-screen">
    <AppHeader @open-settings="settingsOpen = true" />

    <main class="max-w-[900px] mx-auto px-6 py-12">
      <h1 class="text-[28px] font-semibold tracking-tight mb-2 text-gray-900">
        Create Action Items
      </h1>
      <p class="text-gray-600 text-[15px] mb-10">
        Extract action items from meeting notes and create Jira tickets automatically
      </p>

      <!-- Tabs -->
      <div class="flex gap-1 p-1 bg-gray-100 rounded-lg mb-6 border border-gray-200">
        <button
          class="flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all duration-150"
          :class="activeTab === 'create'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-400 hover:text-gray-600'"
          @click="activeTab = 'create'"
        >
          Create from Meeting
        </button>
        <button
          class="flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all duration-150"
          :class="activeTab === 'history'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-400 hover:text-gray-600'"
          @click="activeTab = 'history'"
        >
          History
        </button>
      </div>

      <CreateTab v-if="activeTab === 'create'" />
      <HistoryTab v-else />
    </main>

    <SettingsPanel v-model:open="settingsOpen" />
    <NotificationToast />
  </div>
</template>
