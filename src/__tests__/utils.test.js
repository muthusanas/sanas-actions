import { describe, it, expect } from 'vitest'
import { getInitials, getUniqueValues } from '../utils'

describe('getInitials', () => {
  it('returns initials from full name', () => {
    expect(getInitials('John Smith')).toBe('JS')
  })

  it('handles single name', () => {
    expect(getInitials('John')).toBe('J')
  })

  it('handles multiple names', () => {
    expect(getInitials('John Paul Smith')).toBe('JPS')
  })

  it('returns empty string for null', () => {
    expect(getInitials(null)).toBe('')
  })

  it('returns empty string for undefined', () => {
    expect(getInitials(undefined)).toBe('')
  })

  it('returns empty string for empty string', () => {
    expect(getInitials('')).toBe('')
  })

  it('converts to uppercase', () => {
    expect(getInitials('john smith')).toBe('JS')
  })
})

describe('getUniqueValues', () => {
  it('extracts unique values by key', () => {
    const items = [
      { name: 'John', role: 'dev' },
      { name: 'Jane', role: 'dev' },
      { name: 'Bob', role: 'qa' },
    ]
    expect(getUniqueValues(items, 'role')).toEqual(['dev', 'qa'])
  })

  it('filters out null/undefined values', () => {
    const items = [
      { name: 'John' },
      { name: null },
      { name: 'Jane' },
      { name: undefined },
    ]
    expect(getUniqueValues(items, 'name')).toEqual(['John', 'Jane'])
  })

  it('returns empty array for empty input', () => {
    expect(getUniqueValues([], 'name')).toEqual([])
  })

  it('handles all null values', () => {
    const items = [{ name: null }, { name: null }]
    expect(getUniqueValues(items, 'name')).toEqual([])
  })

  it('preserves order of first occurrence', () => {
    const items = [
      { id: 1, category: 'B' },
      { id: 2, category: 'A' },
      { id: 3, category: 'B' },
      { id: 4, category: 'C' },
    ]
    expect(getUniqueValues(items, 'category')).toEqual(['B', 'A', 'C'])
  })
})
