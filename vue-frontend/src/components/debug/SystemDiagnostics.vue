<template>
  <div class="space-y-4">
    <div v-if="isLoading" class="text-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-red-600 mx-auto"></div>
      <p class="text-sm text-gray-600 mt-2">Running diagnostics...</p>
    </div>
    
    <div v-else class="space-y-3">
      <!-- System Overview -->
      <div class="bg-white rounded-lg border p-3">
        <h5 class="font-medium text-gray-900 mb-2">System Overview</h5>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Uptime:</span>
            <span class="font-mono">{{ systemInfo.uptime }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Version:</span>
            <span class="font-mono">{{ systemInfo.version }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Environment:</span>
            <span class="font-mono">{{ systemInfo.environment }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Debug Mode:</span>
            <span class="font-mono">{{ systemInfo.debugMode ? 'Enabled' : 'Disabled' }}</span>
          </div>
        </div>
      </div>
      
      <!-- Database Status -->
      <div class="bg-white rounded-lg border p-3">
        <h5 class="font-medium text-gray-900 mb-2">Database Status</h5>
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">Connection:</span>
            <span :class="getStatusClass(dbStatus.connected)" class="px-2 py-1 rounded-full text-xs">
              {{ dbStatus.connected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">Tables:</span>
            <span class="text-sm font-mono">{{ dbStatus.tableCount }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">Size:</span>
            <span class="text-sm font-mono">{{ dbStatus.size }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-sm text-gray-600">Last Backup:</span>
            <span class="text-sm font-mono">{{ dbStatus.lastBackup }}</span>
          </div>
        </div>
      </div>
      
      <!-- Service Connectivity -->
      <div class="bg-white rounded-lg border p-3">
        <h5 class="font-medium text-gray-900 mb-2">Service Connectivity</h5>
        <div class="space-y-2">
          <div v-for="service in serviceStatus" :key="service.name" class="flex justify-between items-center">
            <div class="flex items-center">
              <span class="text-sm text-gray-600">{{ service.name }}:</span>
            </div>
            <div class="flex items-center space-x-2">
              <span :class="getStatusClass(service.status)" class="px-2 py-1 rounded-full text-xs">
                {{ service.status }}
              </span>
              <span class="text-xs text-gray-500">{{ service.responseTime }}ms</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Error Log -->
      <div v-if="errorLog.length > 0" class="bg-white rounded-lg border p-3">
        <h5 class="font-medium text-gray-900 mb-2">Recent Errors</h5>
        <div class="space-y-2 max-h-32 overflow-y-auto">
          <div v-for="error in errorLog" :key="error.id" class="text-xs text-red-600">
            <div class="font-medium">{{ error.timestamp }}</div>
            <div>{{ error.message }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Run Diagnostics Button -->
    <button
      @click="runDiagnostics"
      :disabled="isLoading"
      class="w-full mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      🔍 Run System Diagnostics
    </button>
    
    <!-- Last Run -->
    <div class="text-xs text-gray-500 text-center">
      Last run: {{ lastRun }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/services/api'

interface SystemInfo {
  uptime: string
  version: string
  environment: string
  debugMode: boolean
}

interface DBStatus {
  connected: boolean
  tableCount: number
  size: string
  lastBackup: string
}

interface ServiceStatus {
  name: string
  status: string
  responseTime: number
}

interface ErrorLog {
  id: string
  timestamp: string
  message: string
}

const isLoading = ref(false)
const systemInfo = ref<SystemInfo>({
  uptime: 'Unknown',
  version: '1.0.0',
  environment: 'production',
  debugMode: false
})
const dbStatus = ref<DBStatus>({
  connected: false,
  tableCount: 0,
  size: '0 MB',
  lastBackup: 'Never'
})
const serviceStatus = ref<ServiceStatus[]>([])
const errorLog = ref<ErrorLog[]>([])
const lastRun = ref('Never')

const getStatusClass = (status: string | boolean) => {
  if (status === 'ok' || status === true) return 'bg-green-100 text-green-800'
  if (status === 'error' || status === false) return 'bg-red-100 text-red-800'
  return 'bg-yellow-100 text-yellow-800'
}

const runDiagnostics = async () => {
  isLoading.value = true
  try {
    // Check system health
    const healthResult = await apiClient.get('/health')
    if (healthResult.success) {
      // Parse health data
      const health = healthResult.data
      
      // Update system info
      systemInfo.value = {
        uptime: health.uptime || 'Unknown',
        version: health.version || '1.0.0',
        environment: health.environment || 'production',
        debugMode: health.debug_mode || false
      }
      
      // Update database status
      if (health.database) {
        dbStatus.value = {
          connected: health.database.status === 'ok',
          tableCount: health.database.table_count || 0,
          size: health.database.size || '0 MB',
          lastBackup: health.database.last_backup || 'Never'
        }
      }
      
      // Update service status
      serviceStatus.value = [
        {
          name: 'Database',
          status: health.database?.status || 'unknown',
          responseTime: health.database?.response_time || 0
        },
        {
          name: 'Configuration',
          status: health.config?.status || 'unknown',
          responseTime: health.config?.response_time || 0
        },
        {
          name: 'LLM Service',
          status: health.llm?.status || 'unknown',
          responseTime: health.llm?.response_time || 0
        },
        {
          name: 'Authentication',
          status: health.auth?.status || 'unknown',
          responseTime: health.auth?.response_time || 0
        }
      ]
    }
    
    // Check for recent errors (simulated)
    errorLog.value = [
      {
        id: '1',
        timestamp: new Date().toLocaleTimeString(),
        message: 'No recent errors found'
      }
    ]
    
    lastRun.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('Failed to run diagnostics:', error)
    errorLog.value = [
      {
        id: '1',
        timestamp: new Date().toLocaleTimeString(),
        message: 'Failed to run diagnostics: ' + (error as Error).message
      }
    ]
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  runDiagnostics()
})
</script>

