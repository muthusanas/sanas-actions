import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useNotificationStore } from '../../stores/notifications'

describe('useNotificationStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  describe('initial state', () => {
    it('starts not visible', () => {
      const store = useNotificationStore()
      expect(store.visible).toBe(false)
    })

    it('starts with empty message', () => {
      const store = useNotificationStore()
      expect(store.message).toBe('')
    })

    it('starts with default icon', () => {
      const store = useNotificationStore()
      expect(store.icon).toBe('💬')
    })
  })

  describe('show', () => {
    it('makes notification visible', () => {
      const store = useNotificationStore()
      store.show('Test message')
      expect(store.visible).toBe(true)
    })

    it('sets message text', () => {
      const store = useNotificationStore()
      store.show('Test message')
      expect(store.message).toBe('Test message')
    })

    it('uses default icon when not specified', () => {
      const store = useNotificationStore()
      store.show('Test message')
      expect(store.icon).toBe('💬')
    })

    it('allows custom icon', () => {
      const store = useNotificationStore()
      store.show('Test message', '🎉')
      expect(store.icon).toBe('🎉')
    })

    it('auto-hides after timeout', () => {
      const store = useNotificationStore()
      store.show('Test message')

      expect(store.visible).toBe(true)

      vi.runAllTimers()

      expect(store.visible).toBe(false)
    })

    it('resets timer when called again', () => {
      const store = useNotificationStore()

      store.show('First message')
      vi.advanceTimersByTime(1000)

      store.show('Second message')
      vi.advanceTimersByTime(1000)

      // Should still be visible since timer was reset
      expect(store.visible).toBe(true)
      expect(store.message).toBe('Second message')
    })
  })
})
