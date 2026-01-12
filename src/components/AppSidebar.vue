<script setup>
import { ref } from 'vue'

defineProps({
  currentPage: { type: String, default: 'home' },
})

const emit = defineEmits(['navigate', 'collapse-change'])

const collapsed = ref(false)

function toggleCollapse() {
  collapsed.value = !collapsed.value
  emit('collapse-change', collapsed.value)
}

const navItems = [
  { id: 'home', label: 'Action Items', icon: 'clipboard' },
  { id: 'analytics', label: 'Analytics', icon: 'chart' },
  { id: 'settings', label: 'Settings', icon: 'settings' },
]
</script>

<template>
  <aside
    class="fixed left-0 top-0 h-screen bg-white border-r border-gray-200 flex flex-col transition-all duration-300 z-40"
    :class="collapsed ? 'w-16' : 'w-56'"
  >
    <!-- Logo & Hamburger -->
    <div class="p-4 border-b border-gray-200 flex items-center gap-3">
      <button
        class="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors duration-150"
        @click="toggleCollapse"
        :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
      >
        <svg class="w-5 h-5 text-gray-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      <div v-if="!collapsed" class="font-semibold text-base tracking-tight truncate">
        Sanas
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 p-2 space-y-1">
      <button
        v-for="item in navItems"
        :key="item.id"
        class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150"
        :class="currentPage === item.id
          ? 'bg-accent/10 text-accent'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'"
        @click="emit('navigate', item.id)"
        :title="collapsed ? item.label : ''"
      >
        <!-- Clipboard Icon -->
        <svg v-if="item.icon === 'clipboard'" class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
          <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
        </svg>

        <!-- Chart Icon -->
        <svg v-else-if="item.icon === 'chart'" class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>

        <!-- Settings Icon -->
        <svg v-else-if="item.icon === 'settings'" class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3" />
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
        </svg>

        <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
      </button>
    </nav>

    <!-- User -->
    <div class="p-3 border-t border-gray-200">
      <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-accent-light border border-gray-200 flex items-center justify-center text-[13px] font-semibold text-accent flex-shrink-0">
          MK
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <div class="text-sm font-medium text-gray-900 truncate">Muthu K</div>
          <div class="text-xs text-gray-400 truncate">muthu@sanas.ai</div>
        </div>
      </div>
    </div>
  </aside>
</template>
