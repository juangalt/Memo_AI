import { apiClient } from './api'

interface LoginCredentials {
  username: string
  password: string
}

interface AuthResponse {
  session_token: string
  username: string
  is_admin: boolean
  user_id: number
}

export const authService = {
  async login(credentials: LoginCredentials) {
    return apiClient.post<AuthResponse>('/api/v1/auth/login', credentials)
  },

  async validateSession() {
    return apiClient.get<AuthResponse>('/api/v1/auth/validate')
  },

  async logout() {
    return apiClient.post('/api/v1/auth/logout')
  },

  // Admin endpoints
  async listUsers() {
    return apiClient.get('/api/v1/admin/users')
  },

  async createUser(userData: any) {
    return apiClient.post('/api/v1/admin/users/create', userData)
  },

  async deleteUser(username: string) {
    return apiClient.delete(`/api/v1/admin/users/${username}`)
  },

  async getConfig(configName: string) {
    return apiClient.get(`/api/v1/admin/config/${configName}`)
  },

  async updateConfig(configName: string, content: any) {
    return apiClient.put(`/api/v1/admin/config/${configName}`, { content })
  }
}
