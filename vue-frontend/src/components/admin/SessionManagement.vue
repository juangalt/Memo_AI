<template>
  <div class="space-y-4">
    <!-- Current Session Info -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">Current Session</h4>
      <div v-if="currentSession" class="space-y-2">
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">Session ID:</span>
          <span class="text-sm font-mono text-gray-900">{{ currentSession.id }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">User:</span>
          <span class="text-sm text-gray-900">{{ currentSession.username }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">Role:</span>
          <span class="text-sm text-gray-900">
            <span v-if="currentSession.is_admin" class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
              Admin
            </span>
            <span v-else class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
              User
            </span>
          </span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">Created:</span>
          <span class="text-sm text-gray-900">{{ formatDate(currentSession.created_at) }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">Expires:</span>
          <span class="text-sm text-gray-900">{{ formatDate(currentSession.expires_at) }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-sm text-gray-600">Status:</span>
          <span
            :class="currentSession.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            class="px-2 py-1 text-xs rounded-full"
          >
            {{ currentSession.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </div>
      <div v-else class="text-center text-gray-500">
        No active session
      </div>
    </div>
    
    <!-- Session Actions -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">Session Actions</h4>
      <div class="space-y-3">
        <button
          @click="refreshSession"
          :disabled="isRefreshing"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {{ isRefreshing ? 'Refreshing...' : '🔄 Refresh Session' }}
        </button>
        
        <button
          @click="logout"
          :disabled="isLoggingOut"
          class="w-full px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
        >
          {{ isLoggingOut ? 'Logging out...' : '🚪 Logout' }}
        </button>
      </div>
    </div>
    
    <!-- Session Statistics -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">Session Statistics</h4>
      <div class="grid grid-cols-2 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold text-blue-600">{{ sessionAge }}</div>
          <div class="text-sm text-gray-600">Session Age</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ timeRemaining }}</div>
          <div class="text-sm text-gray-600">Time Remaining</div>
        </div>
      </div>
    </div>
    
    <!-- Session Health -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">Session Health</h4>
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Session Valid:</span>
          <span
            :class="isSessionValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            class="px-2 py-1 text-xs rounded-full"
          >
            {{ isSessionValid ? 'Valid' : 'Invalid' }}
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600">Expires Soon:</span>
          <span
            :class="expiresSoon ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'"
            class="px-2 py-1 text-xs rounded-full"
          >
            {{ expiresSoon ? 'Yes' : 'No' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api'
import { authService } from '@/services/auth'
import { configService } from '@/services/config'

interface Session {
  id: string
  username: string
  is_admin: boolean
  is_active: boolean
  created_at: string
  expires_at: string
}

const router = useRouter()
const authStore = useAuthStore()

const currentSession = ref<Session | null>(null)
const isRefreshing = ref(false)
const isLoggingOut = ref(false)
const sessionTimer = ref<number | null>(null)
const frontendConfig = ref<any>(null)

const sessionAge = computed(() => {
  if (!currentSession.value) return 'N/A'
  // Parse UTC dates correctly by appending 'Z' if not present
  const createdStr = currentSession.value.created_at.endsWith('Z') ? currentSession.value.created_at : currentSession.value.created_at + 'Z'
  const created = new Date(createdStr)
  const now = new Date()
  const diff = Math.floor((now.getTime() - created.getTime()) / 1000 / 60) // minutes
  return `${diff}m`
})

const timeRemaining = computed(() => {
  if (!currentSession.value) return 'N/A'
  // Parse UTC dates correctly by appending 'Z' if not present
  const expiresStr = currentSession.value.expires_at.endsWith('Z') ? currentSession.value.expires_at : currentSession.value.expires_at + 'Z'
  const expires = new Date(expiresStr)
  const now = new Date()
  const diff = Math.floor((expires.getTime() - now.getTime()) / 1000 / 60) // minutes
  return diff > 0 ? `${diff}m` : 'Expired'
})

const isSessionValid = computed(() => {
  if (!currentSession.value) return false
  // Parse UTC dates correctly by appending 'Z' if not present
  const expiresStr = currentSession.value.expires_at.endsWith('Z') ? currentSession.value.expires_at : currentSession.value.expires_at + 'Z'
  const expires = new Date(expiresStr)
  const now = new Date()
  return expires > now && currentSession.value.is_active
})

const expiresSoon = computed(() => {
  if (!currentSession.value) return false
  // Parse UTC dates correctly by appending 'Z' if not present
  const expiresStr = currentSession.value.expires_at.endsWith('Z') ? currentSession.value.expires_at : currentSession.value.expires_at + 'Z'
  const expires = new Date(expiresStr)
  const now = new Date()
  const diff = Math.floor((expires.getTime() - now.getTime()) / 1000 / 60) // minutes
  return diff > 0 && diff <= (frontendConfig.value?.session_warning_threshold || 10) // expires within configured threshold
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const loadCurrentSession = async () => {
  try {
    // Get current session info from auth store or API
    if (authStore.user) {
      // Validate session to get real session data including expires_at
      const result = await authStore.validateSession()
      if (result) {
        // Get session data from the validate response
        const response = await authService.validateSession()
        if (response.success && response.data) {
          currentSession.value = {
            id: 'current-session',
            username: response.data.username,
            is_admin: response.data.is_admin,
            is_active: true,
            created_at: response.data.created_at,
            expires_at: response.data.expires_at
          }
        }
      }
    }
  } catch (error) {
    console.error('Failed to load session info:', error)
  }
}

const refreshSession = async () => {
  isRefreshing.value = true
  try {
    // Validate current session to refresh it
    const result = await authStore.validateSession()
    if (result) {
      await loadCurrentSession()
    }
  } catch (error) {
    console.error('Failed to refresh session:', error)
  } finally {
    isRefreshing.value = false
  }
}

const logout = async () => {
  isLoggingOut.value = true
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Failed to logout:', error)
  } finally {
    isLoggingOut.value = false
  }
}

const loadFrontendConfig = async () => {
  try {
    frontendConfig.value = await configService.getFrontendConfig()
  } catch (error) {
    console.error('Failed to load frontend configuration:', error)
  }
}

const startSessionTimer = () => {
  // Update session info every configured interval
  const interval = frontendConfig.value?.session_refresh_interval || 60000
  sessionTimer.value = window.setInterval(() => {
    loadCurrentSession()
  }, interval * 1000) // Convert seconds to milliseconds
}

onMounted(async () => {
  await loadFrontendConfig()
  loadCurrentSession()
  startSessionTimer()
})

onUnmounted(() => {
  if (sessionTimer.value) {
    clearInterval(sessionTimer.value)
  }
})
</script>

