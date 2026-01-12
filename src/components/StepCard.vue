<script setup>
defineProps({
  step: { type: Number, required: true },
  title: { type: String, required: true },
  active: { type: Boolean, default: false },
  completed: { type: Boolean, default: false },
  success: { type: Boolean, default: false },
})
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
    <div class="flex items-center gap-4 px-6 py-5 border-b border-gray-200 bg-gray-50">
      <div
        class="w-7 h-7 rounded-full flex items-center justify-center text-[13px] font-semibold flex-shrink-0 border-2"
        :class="{
          'bg-accent border-accent text-white': active && !success,
          'bg-accent-light border-accent text-accent': completed,
          'bg-white border-gray-200 text-gray-400': !active && !completed,
        }"
      >
        <template v-if="success || completed">✓</template>
        <template v-else>{{ step }}</template>
      </div>
      <div class="text-[15px] font-medium">{{ title }}</div>
      <div class="ml-auto">
        <slot name="badge" />
      </div>
    </div>
    <div class="p-6">
      <slot />
    </div>
    <slot name="footer" />
  </div>
</template>
