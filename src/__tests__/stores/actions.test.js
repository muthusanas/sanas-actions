import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useActionsStore } from '../../stores/actions'

describe('useActionsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  describe('initial state', () => {
    it('starts at step 1', () => {
      const store = useActionsStore()
      expect(store.currentStep).toBe(1)
    })

    it('starts not loading', () => {
      const store = useActionsStore()
      expect(store.loading).toBe(false)
    })

    it('starts with empty actions', () => {
      const store = useActionsStore()
      expect(store.actions).toEqual([])
    })

    it('has default config values', () => {
      const store = useActionsStore()
      expect(store.config.project).toBe('SANAS')
      expect(store.config.issueType).toBe('Task')
      expect(store.config.label).toBe('meeting-action')
    })
  })

  describe('extractActions', () => {
    it('does nothing if notionUrl is empty', () => {
      const store = useActionsStore()
      store.notionUrl = ''
      store.extractActions()
      expect(store.currentStep).toBe(1)
      expect(store.loading).toBe(false)
    })

    it('sets loading and advances to step 2', () => {
      const store = useActionsStore()
      store.notionUrl = 'https://notion.so/test'
      store.extractActions()
      expect(store.currentStep).toBe(2)
      expect(store.loading).toBe(true)
    })

    it('populates actions after timeout', () => {
      const store = useActionsStore()
      store.notionUrl = 'https://notion.so/test'
      store.extractActions()

      vi.runAllTimers()

      expect(store.loading).toBe(false)
      expect(store.actions.length).toBe(5)
    })
  })

  describe('toggleAction', () => {
    it('toggles selected state', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1, selected: true }]

      store.toggleAction(0)
      expect(store.actions[0].selected).toBe(false)

      store.toggleAction(0)
      expect(store.actions[0].selected).toBe(true)
    })
  })

  describe('removeAction', () => {
    it('removes action at index', () => {
      const store = useActionsStore()
      store.actions = [
        { id: 1, title: 'First' },
        { id: 2, title: 'Second' },
        { id: 3, title: 'Third' },
      ]

      store.removeAction(1)

      expect(store.actions.length).toBe(2)
      expect(store.actions[0].title).toBe('First')
      expect(store.actions[1].title).toBe('Third')
    })

    it('handles removing first item', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1 }, { id: 2 }]

      store.removeAction(0)

      expect(store.actions.length).toBe(1)
      expect(store.actions[0].id).toBe(2)
    })

    it('handles removing last item', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1 }, { id: 2 }]

      store.removeAction(1)

      expect(store.actions.length).toBe(1)
      expect(store.actions[0].id).toBe(1)
    })
  })

  describe('assignAction', () => {
    it('assigns assignee to action', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1, assignee: null }]

      store.assignAction(0, 'John Smith')

      expect(store.actions[0].assignee).toBe('John Smith')
    })

    it('can reassign to different assignee', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1, assignee: 'John Smith' }]

      store.assignAction(0, 'Jane Doe')

      expect(store.actions[0].assignee).toBe('Jane Doe')
    })
  })

  describe('createTickets', () => {
    it('creates tickets only for selected actions', () => {
      const store = useActionsStore()
      store.actions = [
        { id: 1, selected: true, assignee: 'John' },
        { id: 2, selected: false, assignee: 'Jane' },
        { id: 3, selected: true, assignee: 'Bob' },
      ]

      store.createTickets()

      expect(store.createdTickets.length).toBe(2)
    })

    it('generates ticket keys with project prefix', () => {
      const store = useActionsStore()
      store.config.project = 'TEST'
      store.actions = [{ id: 1, selected: true, assignee: 'John' }]

      store.createTickets()

      expect(store.createdTickets[0].key).toMatch(/^TEST-\d+$/)
    })

    it('advances to step 3', () => {
      const store = useActionsStore()
      store.actions = [{ id: 1, selected: true, assignee: 'John' }]

      store.createTickets()

      expect(store.currentStep).toBe(3)
    })
  })

  describe('reset', () => {
    it('resets all state to initial values', () => {
      const store = useActionsStore()
      store.currentStep = 3
      store.loading = true
      store.notionUrl = 'https://notion.so/test'
      store.actions = [{ id: 1 }]
      store.createdTickets = [{ key: 'TEST-1' }]

      store.reset()

      expect(store.currentStep).toBe(1)
      expect(store.loading).toBe(false)
      expect(store.notionUrl).toBe('')
      expect(store.actions).toEqual([])
      expect(store.createdTickets).toEqual([])
    })

    it('clears pending timeouts', () => {
      const store = useActionsStore()
      store.actions = [
        { id: 1, selected: true, assignee: 'John' },
        { id: 2, selected: true, assignee: 'Jane' },
      ]

      store.createTickets()
      store.reset()

      // Timeouts should be cleared, not throw errors
      expect(() => vi.runAllTimers()).not.toThrow()
    })
  })
})
