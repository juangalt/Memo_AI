import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

interface User {
  id: number
  username: string
  is_admin: boolean
}

interface AuthState {
  user: User | null
  sessionToken: string | null
  isLoading: boolean
  error: string | null
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  // Store token in memory only (never localStorage per auth specs)
  const sessionToken = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const username = computed(() => user.value?.username || '')

  // Actions
  const login = async (username: string, password: string) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await authService.login({ username, password })

      if (result.success && result.data) {
        // Handle successful login
        user.value = {
          id: result.data.user_id,
          username: result.data.username,
          is_admin: result.data.is_admin
        }
        sessionToken.value = result.data.session_token
        return { success: true }
      } else {
        // Handle authentication errors per auth specs
        if (result.status && typeof result.status === 'string') {
          // Handle auth spec error codes
          if (result.status === 'AUTH_ACCOUNT_LOCKED') {
            error.value = 'Account temporarily locked due to multiple failed attempts. Please try again later.'
          } else if (result.status === 'AUTH_INVALID_CREDENTIALS') {
            error.value = 'Invalid username or password.'
          } else {
            error.value = result.error || 'Login failed. Please try again.'
          }
        } else {
          error.value = result.error || 'Login failed. Please try again.'
        }
        return { success: false, error: error.value, code: result.status }
      }
    } catch (err: any) {
      error.value = 'Login failed. Please try again.'
      return { success: false, error: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const validateSession = async (): Promise<boolean> => {
    if (!sessionToken.value) return false

    try {
      const result = await authService.validateSession()

      if (result.success && result.data) {
        // Update user info from validation response
        user.value = {
          id: result.data.user_id,
          username: result.data.username,
          is_admin: result.data.is_admin
        }
        return true
      } else {
        // Handle session validation errors per auth specs
        if (result.status && typeof result.status === 'string') {
          if (result.status === 'AUTH_SESSION_EXPIRED' || result.status === 'AUTH_INVALID_TOKEN') {
            logout()
            return false
          }
        }
        return false
      }
    } catch (err) {
      // Clear session on validation error
      logout()
      return false
    }
  }

  const logout = async () => {
    try {
      // Attempt server-side logout
      await authService.logout()
    } catch (err) {
      // Ignore logout errors - session will expire naturally
      console.warn('Logout request failed, clearing local session anyway')
    } finally {
      // Always clear local session state
      user.value = null
      sessionToken.value = null
      error.value = null
    }
  }

  // Initialize from memory if available (not localStorage per auth specs)
  const initializeFromMemory = () => {
    // Token should be passed from previous session or login
    // Per auth specs: store in memory only, never persistent storage
    // This method is called during app initialization
  }

  return {
    // State
    user,
    sessionToken,
    isLoading,
    error,

    // Getters
    isAuthenticated,
    isAdmin,
    username,

    // Actions
    login,
    validateSession,
    logout,
    initializeFromMemory
  }
})
