// API configuration and service functions
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`

  // Don't set Content-Type for FormData (let browser handle it)
  const isFormData = options.body instanceof FormData
  const defaultHeaders = isFormData ? {} : { 'Content-Type': 'application/json' }

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }

  try {
    const response = await fetch(url, config)

    if (!response.ok) {
      let errorData = null
      try {
        errorData = await response.json()
      } catch {
        // Response may not be JSON
      }
      throw new ApiError(
        errorData?.detail || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return null
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError(error.message || 'Network error', 0)
  }
}

// Actions API
export const actionsApi = {
  async extractFromText(content) {
    return fetchApi('/api/actions/extract', {
      method: 'POST',
      body: JSON.stringify({
        input_type: 'text',
        content,
      }),
    })
  },

  async extractFromFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    return fetchApi('/api/actions/extract-file', {
      method: 'POST',
      body: formData,
    })
  },

  async createTickets(actionIds, config) {
    return fetchApi('/api/actions/tickets', {
      method: 'POST',
      body: JSON.stringify({
        action_ids: actionIds,
        config: {
          project: config.project,
          issue_type: config.issueType,
          label: config.label,
        },
      }),
    })
  },
}

// Notifications API
export const notificationsApi = {
  async sendNotification(assignee, message, ticketKey = null) {
    return fetchApi('/api/notifications/send', {
      method: 'POST',
      body: JSON.stringify({
        assignee,
        message,
        ticket_key: ticketKey,
      }),
    })
  },

  async sendReminders(assignees) {
    return fetchApi('/api/notifications/reminders', {
      method: 'POST',
      body: JSON.stringify({
        assignees,
      }),
    })
  },
}

// Settings API
export const settingsApi = {
  async getSettings() {
    return fetchApi('/api/settings')
  },

  async updateSettings(settings) {
    return fetchApi('/api/settings', {
      method: 'PUT',
      body: JSON.stringify(settings),
    })
  },

  async getTeamMembers() {
    return fetchApi('/api/team')
  },

  async addTeamMember(member) {
    return fetchApi('/api/team', {
      method: 'POST',
      body: JSON.stringify(member),
    })
  },

  async updateTeamMember(id, updates) {
    return fetchApi(`/api/team/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  },

  async deleteTeamMember(id) {
    return fetchApi(`/api/team/${id}`, {
      method: 'DELETE',
    })
  },

  async getIntegrationStatus() {
    return fetchApi('/api/integrations/status')
  },
}

// Analytics API
export const analyticsApi = {
  async getAnalytics() {
    return fetchApi('/api/analytics')
  },
}

// Health check
export async function checkHealth() {
  return fetchApi('/health')
}

export { ApiError }
