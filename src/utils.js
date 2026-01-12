/**
 * Generate initials from a full name
 * @param {string} name - Full name (e.g., "John Smith")
 * @returns {string} Initials (e.g., "JS")
 */
export function getInitials(name) {
  if (!name) return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

/**
 * Get unique values from an array of objects by a specific key
 * @param {Array} items - Array of objects
 * @param {string} key - Property key to extract unique values from
 * @returns {Array} Array of unique values
 */
export function getUniqueValues(items, key) {
  return [...new Set(items.filter(item => item[key]).map(item => item[key]))]
}
