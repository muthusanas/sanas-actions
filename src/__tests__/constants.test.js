import { describe, it, expect } from 'vitest'
import { TIMING, TICKET, TEAM_MEMBERS } from '../constants'

describe('TIMING constants', () => {
  it('has API_SIMULATION_DELAY defined as positive number', () => {
    expect(TIMING.API_SIMULATION_DELAY).toBeGreaterThan(0)
    expect(typeof TIMING.API_SIMULATION_DELAY).toBe('number')
  })

  it('has NOTIFICATION_DISPLAY_DURATION defined as positive number', () => {
    expect(TIMING.NOTIFICATION_DISPLAY_DURATION).toBeGreaterThan(0)
    expect(typeof TIMING.NOTIFICATION_DISPLAY_DURATION).toBe('number')
  })

  it('has NOTIFICATION_STAGGER_DELAY defined as positive number', () => {
    expect(TIMING.NOTIFICATION_STAGGER_DELAY).toBeGreaterThan(0)
    expect(typeof TIMING.NOTIFICATION_STAGGER_DELAY).toBe('number')
  })
})

describe('TICKET constants', () => {
  it('has STARTING_NUMBER defined as positive integer', () => {
    expect(TICKET.STARTING_NUMBER).toBeGreaterThan(0)
    expect(Number.isInteger(TICKET.STARTING_NUMBER)).toBe(true)
  })
})

describe('TEAM_MEMBERS', () => {
  it('is a non-empty array', () => {
    expect(Array.isArray(TEAM_MEMBERS)).toBe(true)
    expect(TEAM_MEMBERS.length).toBeGreaterThan(0)
  })

  it('each member has initials and name', () => {
    TEAM_MEMBERS.forEach(member => {
      expect(member).toHaveProperty('initials')
      expect(member).toHaveProperty('name')
      expect(typeof member.initials).toBe('string')
      expect(typeof member.name).toBe('string')
      expect(member.initials.length).toBeGreaterThan(0)
      expect(member.name.length).toBeGreaterThan(0)
    })
  })
})
