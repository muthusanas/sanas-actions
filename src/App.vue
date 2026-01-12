<script setup>
import { ref } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import CreateTab from './components/CreateTab.vue'
import AnalyticsPage from './components/AnalyticsPage.vue'
import SettingsPage from './components/SettingsPage.vue'
import NotificationToast from './components/NotificationToast.vue'

const currentPage = ref('home')
const sidebarCollapsed = ref(false)

function handleNavigate(page) {
  currentPage.value = page
}
</script>

<template>
  <div class="min-h-screen">
    <AppSidebar
      :current-page="currentPage"
      @navigate="handleNavigate"
      @collapse-change="sidebarCollapsed = $event"
    />

    <main
      class="min-h-screen bg-gray-50 transition-all duration-300"
      :class="sidebarCollapsed ? 'ml-16' : 'ml-56'"
    >
      <div class="px-8 py-10">
        <!-- Home / Action Items Page -->
        <template v-if="currentPage === 'home'">
          <h1 class="text-[28px] font-semibold tracking-tight mb-2 text-gray-900">
            Create Action Items
          </h1>
          <p class="text-gray-600 text-[15px] mb-10">
            Extract action items from meeting notes and create Jira tickets automatically
          </p>
          <CreateTab />
        </template>

        <!-- Analytics Page -->
        <AnalyticsPage v-else-if="currentPage === 'analytics'" />

        <!-- Settings Page -->
        <SettingsPage v-else-if="currentPage === 'settings'" />
      </div>
    </main>

    <NotificationToast />
  </div>
</template>
