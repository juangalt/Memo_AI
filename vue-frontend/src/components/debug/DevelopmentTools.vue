<template>
  <div class="space-y-4">
    <!-- Console Output -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Console Output</h5>
      <div class="bg-black text-green-400 p-3 rounded font-mono text-sm h-32 overflow-y-auto">
        <div v-for="log in consoleLogs" :key="log.id" class="mb-1">
          <span class="text-gray-500">[{{ log.timestamp }}]</span>
          <span :class="getLogLevelClass(log.level)" class="ml-2">{{ log.level.toUpperCase() }}:</span>
          <span class="ml-2">{{ log.message }}</span>
        </div>
      </div>
      <div class="flex justify-between items-center mt-2">
        <button
          @click="clearConsole"
          class="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Clear Console
        </button>
        <span class="text-xs text-gray-500">{{ consoleLogs.length }} log entries</span>
      </div>
    </div>
    
    <!-- Environment Info -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Environment Information</h5>
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span class="text-gray-600">Node Version:</span>
          <span class="font-mono ml-2">{{ envInfo.nodeVersion }}</span>
        </div>
        <div>
          <span class="text-gray-600">NPM Version:</span>
          <span class="font-mono ml-2">{{ envInfo.npmVersion }}</span>
        </div>
        <div>
          <span class="text-gray-600">Vue Version:</span>
          <span class="font-mono ml-2">{{ envInfo.vueVersion }}</span>
        </div>
        <div>
          <span class="text-gray-600">Build Mode:</span>
          <span class="font-mono ml-2">{{ envInfo.buildMode }}</span>
        </div>
        <div>
          <span class="text-gray-600">API Base URL:</span>
          <span class="font-mono ml-2">{{ envInfo.apiBaseUrl }}</span>
        </div>
        <div>
          <span class="text-gray-600">Debug Mode:</span>
          <span class="font-mono ml-2">{{ envInfo.debugMode ? 'Enabled' : 'Disabled' }}</span>
        </div>
      </div>
    </div>
    
    <!-- Debug Actions -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Debug Actions</h5>
      <div class="grid grid-cols-2 gap-3">
        <button
          @click="testAuthStore"
          class="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Test Auth Store
        </button>
        <button
          @click="testApiClient"
          class="px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700"
        >
          Test API Client
        </button>
        <button
          @click="clearLocalStorage"
          class="px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
        >
          Clear Local Storage
        </button>
        <button
          @click="exportDebugData"
          class="px-3 py-2 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
        >
          Export Debug Data
        </button>
        <button
          @click="simulateError"
          class="px-3 py-2 text-sm bg-orange-600 text-white rounded hover:bg-orange-700"
        >
          Simulate Error
        </button>
        <button
          @click="testRouter"
          class="px-3 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Test Router
        </button>
      </div>
    </div>
    
    <!-- Component State -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Component State</h5>
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Auth Store:</span>
          <span :class="getStatusClass(componentState.authStore)" class="px-2 py-1 rounded text-xs">
            {{ componentState.authStore ? 'Initialized' : 'Not Initialized' }}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">API Client:</span>
          <span :class="getStatusClass(componentState.apiClient)" class="px-2 py-1 rounded text-xs">
            {{ componentState.apiClient ? 'Connected' : 'Not Connected' }}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Router:</span>
          <span :class="getStatusClass(componentState.router)" class="px-2 py-1 rounded text-xs">
            {{ componentState.router ? 'Active' : 'Not Active' }}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Pinia Store:</span>
          <span :class="getStatusClass(componentState.piniaStore)" class="px-2 py-1 rounded text-xs">
            {{ componentState.piniaStore ? 'Initialized' : 'Not Initialized' }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Network Status -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Network Status</h5>
      <div class="space-y-2">
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Online Status:</span>
          <span :class="getStatusClass(networkStatus.online)" class="px-2 py-1 rounded text-xs">
            {{ networkStatus.online ? 'Online' : 'Offline' }}
          </span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Connection Type:</span>
          <span class="text-sm font-mono">{{ networkStatus.connectionType }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-600">Effective Type:</span>
          <span class="text-sm font-mono">{{ networkStatus.effectiveType }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { apiClient } from '@/services/api'
import { configService } from '@/services/config'

interface ConsoleLog {
  id: string
  timestamp: string
  level: 'info' | 'warn' | 'error' | 'debug'
  message: string
}

interface EnvInfo {
  nodeVersion: string
  npmVersion: string
  vueVersion: string
  buildMode: string
  apiBaseUrl: string
  debugMode: boolean
}

interface ComponentState {
  authStore: boolean
  apiClient: boolean
  router: boolean
  piniaStore: boolean
}

interface NetworkStatus {
  online: boolean
  connectionType: string
  effectiveType: string
}

const router = useRouter()
const authStore = useAuthStore()

const consoleLogs = ref<ConsoleLog[]>([])
const frontendConfig = ref<any>(null)
const envInfo = ref<EnvInfo>({
  nodeVersion: '18.x',
  npmVersion: '9.x',
  vueVersion: '3.x',
  buildMode: import.meta.env.MODE,
  apiBaseUrl: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
  debugMode: import.meta.env.DEV
})
const componentState = ref<ComponentState>({
  authStore: false,
  apiClient: false,
  router: false,
  piniaStore: false
})
const networkStatus = ref<NetworkStatus>({
  online: navigator.onLine,
  connectionType: 'unknown',
  effectiveType: 'unknown'
})

const getLogLevelClass = (level: string) => {
  switch (level) {
    case 'error': return 'text-red-400'
    case 'warn': return 'text-yellow-400'
    case 'debug': return 'text-blue-400'
    default: return 'text-green-400'
  }
}

const getStatusClass = (status: boolean) => {
  return status ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
}

const addLog = (level: 'info' | 'warn' | 'error' | 'debug', message: string) => {
  consoleLogs.value.push({
    id: Date.now().toString(),
    timestamp: new Date().toLocaleTimeString(),
    level,
    message
  })
  
  // Keep only last configured number of logs
  const logLimit = frontendConfig.value?.debug_console_log_limit || 50
  if (consoleLogs.value.length > logLimit) {
    consoleLogs.value = consoleLogs.value.slice(-logLimit)
  }
}

const loadFrontendConfig = async () => {
  try {
    frontendConfig.value = await configService.getFrontendConfig()
  } catch (error) {
    console.error('Failed to load frontend configuration:', error)
  }
}

const clearConsole = () => {
  consoleLogs.value = []
  addLog('info', 'Console cleared')
}

const testAuthStore = async () => {
  addLog('info', 'Testing auth store...')
  try {
    componentState.value.authStore = !!authStore
    componentState.value.piniaStore = true
    addLog('info', `Auth store test: ${authStore.isAuthenticated ? 'Authenticated' : 'Not authenticated'}`)
  } catch (error) {
    addLog('error', `Auth store test failed: ${(error as Error).message}`)
  }
}

const testApiClient = async () => {
  addLog('info', 'Testing API client...')
  try {
    const result = await apiClient.get('/health')
    componentState.value.apiClient = result.success
    addLog('info', `API client test: ${result.success ? 'Success' : 'Failed'}`)
  } catch (error) {
    addLog('error', `API client test failed: ${(error as Error).message}`)
  }
}

const clearLocalStorage = () => {
  addLog('info', 'Clearing local storage...')
  try {
    localStorage.clear()
    addLog('info', 'Local storage cleared successfully')
  } catch (error) {
    addLog('error', `Failed to clear local storage: ${(error as Error).message}`)
  }
}

const exportDebugData = () => {
  addLog('info', 'Exporting debug data...')
  try {
    const debugData = {
      timestamp: new Date().toISOString(),
      envInfo: envInfo.value,
      componentState: componentState.value,
      networkStatus: networkStatus.value,
      consoleLogs: consoleLogs.value
    }
    
    const blob = new Blob([JSON.stringify(debugData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `debug-data-${Date.now()}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    addLog('info', 'Debug data exported successfully')
  } catch (error) {
    addLog('error', `Failed to export debug data: ${(error as Error).message}`)
  }
}

const simulateError = () => {
  addLog('warn', 'Simulating error...')
  try {
    throw new Error('This is a simulated error for testing purposes')
  } catch (error) {
    addLog('error', `Simulated error: ${(error as Error).message}`)
  }
}

const testRouter = () => {
  addLog('info', 'Testing router...')
  try {
    componentState.value.router = !!router
    addLog('info', `Router test: ${router.currentRoute.value.path}`)
  } catch (error) {
    addLog('error', `Router test failed: ${(error as Error).message}`)
  }
}

const updateNetworkStatus = () => {
  networkStatus.value.online = navigator.onLine
  
  if ('connection' in navigator) {
    const connection = (navigator as any).connection
    networkStatus.value.connectionType = connection.effectiveType || 'unknown'
    networkStatus.value.effectiveType = connection.effectiveType || 'unknown'
  }
}

onMounted(async () => {
  await loadFrontendConfig()
  addLog('info', 'Development tools initialized')
  
  // Test components
  testAuthStore()
  testApiClient()
  testRouter()
  
  // Update network status
  updateNetworkStatus()
  
  // Listen for network changes
  window.addEventListener('online', updateNetworkStatus)
  window.addEventListener('offline', updateNetworkStatus)
})

onUnmounted(() => {
  window.removeEventListener('online', updateNetworkStatus)
  window.removeEventListener('offline', updateNetworkStatus)
})
</script>

