<script setup>
defineProps({
  tickets: { type: Array, default: () => [] },
})

defineEmits(['reset'])
</script>

<template>
  <div class="text-center py-12">
    <div class="w-16 h-16 bg-accent-light rounded-full flex items-center justify-center text-[32px] mx-auto mb-6 text-accent">
      ✓
    </div>
    <div class="text-xl font-semibold mb-2">{{ tickets.length }} tickets created in Jira</div>
    <div class="text-gray-600 text-sm mb-6">
      Slack notifications sent to {{ new Set(tickets.filter(t => t.assignee).map(t => t.assignee)).size }} team members
    </div>

    <div class="flex flex-col gap-2 max-w-[400px] mx-auto my-6">
      <a
        v-for="ticket in tickets"
        :key="ticket.key"
        href="#"
        class="flex items-center justify-between px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg no-underline text-gray-900 transition-all duration-150 hover:border-accent hover:bg-accent/5"
      >
        <span class="font-mono text-[13px] text-accent font-medium">{{ ticket.key }}</span>
        <span class="text-[13px] text-gray-400">{{ ticket.assignee || '—' }}</span>
      </a>
    </div>

    <button class="btn btn-secondary" @click="$emit('reset')">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="1 4 1 10 7 10" />
        <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
      </svg>
      Create More
    </button>
  </div>
</template>
