import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSettingsStore } from '../../stores/settings'

describe('useSettingsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('reminders', () => {
    it('has enabled default to true', () => {
      const store = useSettingsStore()
      expect(store.reminders.enabled).toBe(true)
    })

    it('has default frequency', () => {
      const store = useSettingsStore()
      expect(store.reminders.frequency).toBe('Weekly')
    })

    it('has default day', () => {
      const store = useSettingsStore()
      expect(store.reminders.day).toBe('Monday')
    })

    it('has default time', () => {
      const store = useSettingsStore()
      expect(store.reminders.time).toBe('9:00 AM')
    })

    it('allows updating settings', () => {
      const store = useSettingsStore()

      store.reminders.enabled = false
      store.reminders.frequency = 'Daily'

      expect(store.reminders.enabled).toBe(false)
      expect(store.reminders.frequency).toBe('Daily')
    })
  })

  describe('notifications', () => {
    it('has onCreate default to true', () => {
      const store = useSettingsStore()
      expect(store.notifications.onCreate).toBe(true)
    })

    it('has overdueWarnings default to true', () => {
      const store = useSettingsStore()
      expect(store.notifications.overdueWarnings).toBe(true)
    })

    it('allows toggling settings', () => {
      const store = useSettingsStore()

      store.notifications.onCreate = false

      expect(store.notifications.onCreate).toBe(false)
    })
  })

  describe('defaults', () => {
    it('has default project', () => {
      const store = useSettingsStore()
      expect(store.defaults.project).toBe('SANAS')
    })

    it('has default issue type', () => {
      const store = useSettingsStore()
      expect(store.defaults.issueType).toBe('Task')
    })

    it('allows updating defaults', () => {
      const store = useSettingsStore()

      store.defaults.project = 'INFRA'
      store.defaults.issueType = 'Bug'

      expect(store.defaults.project).toBe('INFRA')
      expect(store.defaults.issueType).toBe('Bug')
    })
  })
})
