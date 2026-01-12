<script setup>
import { useNotificationStore } from '../stores/notifications'

const notifications = useNotificationStore()
</script>

<template>
  <div
    class="fixed bottom-6 right-6 bg-white border border-gray-200 rounded-lg px-5 py-4 flex items-center gap-3 shadow-lg transition-all duration-300 z-[300]"
    :class="notifications.visible ? 'translate-y-0 opacity-100' : 'translate-y-[100px] opacity-0'"
  >
    <span class="text-xl">{{ notifications.icon }}</span>
    <span class="text-sm">{{ notifications.message }}</span>
  </div>
</template>
