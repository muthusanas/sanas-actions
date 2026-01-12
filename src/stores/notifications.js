import { defineStore } from 'pinia'
import { ref } from 'vue'
import { TIMING } from '../constants'

export const useNotificationStore = defineStore('notifications', () => {
  const visible = ref(false)
  const message = ref('')
  const icon = ref('💬')

  let hideTimeoutId = null

  function show(text, iconEmoji = '💬') {
    message.value = text
    icon.value = iconEmoji
    visible.value = true

    if (hideTimeoutId) {
      clearTimeout(hideTimeoutId)
    }

    hideTimeoutId = setTimeout(() => {
      visible.value = false
    }, TIMING.NOTIFICATION_DISPLAY_DURATION)
  }

  return {
    visible,
    message,
    icon,
    show,
  }
})
