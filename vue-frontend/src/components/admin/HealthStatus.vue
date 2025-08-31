<template>
  <div class="space-y-4">
    <div v-if="isLoading" class="text-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
      <p class="text-sm text-gray-600 mt-2">Checking system health...</p>
    </div>
    
    <div v-else class="space-y-3">
      <!-- Overall Health -->
      <div class="flex items-center justify-between p-3 bg-white rounded-lg border">
        <div class="flex items-center">
          <span class="text-lg mr-2">🏥</span>
          <span class="font-medium">Overall System</span>
        </div>
        <span :class="overallStatusClass" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ overallStatus }}
        </span>
      </div>
      
      <!-- Database Health -->
      <div class="flex items-center justify-between p-3 bg-white rounded-lg border">
        <div class="flex items-center">
          <span class="text-lg mr-2">🗄️</span>
          <span class="font-medium">Database</span>
        </div>
        <span :class="getStatusClass(healthData.database?.status)" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ healthData.database?.status || 'Unknown' }}
        </span>
      </div>
      
      <!-- Configuration Health -->
      <div class="flex items-center justify-between p-3 bg-white rounded-lg border">
        <div class="flex items-center">
          <span class="text-lg mr-2">⚙️</span>
          <span class="font-medium">Configuration</span>
        </div>
        <span :class="getStatusClass(healthData.config?.status)" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ healthData.config?.status || 'Unknown' }}
        </span>
      </div>
      
      <!-- LLM Health -->
      <div class="flex items-center justify-between p-3 bg-white rounded-lg border">
        <div class="flex items-center">
          <span class="text-lg mr-2">🤖</span>
          <span class="font-medium">LLM Service</span>
        </div>
        <span :class="getStatusClass(healthData.llm?.status)" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ healthData.llm?.status || 'Unknown' }}
        </span>
      </div>
      
      <!-- Auth Health -->
      <div class="flex items-center justify-between p-3 bg-white rounded-lg border">
        <div class="flex items-center">
          <span class="text-lg mr-2">🔐</span>
          <span class="font-medium">Authentication</span>
        </div>
        <span :class="getStatusClass(healthData.auth?.status)" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ healthData.auth?.status || 'Unknown' }}
        </span>
      </div>
    </div>
    
    <!-- Refresh Button -->
    <button
      @click="checkHealth"
      :disabled="isLoading"
      class="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      🔄 Refresh Health Status
    </button>
    
    <!-- Last Updated -->
    <div class="text-xs text-gray-500 text-center">
      Last updated: {{ lastUpdated }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface HealthData {
  database?: { status: string; details?: string }
  config?: { status: string; details?: string }
  llm?: { status: string; details?: string }
  auth?: { status: string; details?: string }
}

const isLoading = ref(false)
const healthData = ref<HealthData>({})
const lastUpdated = ref('Never')

const overallStatus = computed(() => {
  const statuses = Object.values(healthData.value).map(service => service?.status)
  if (statuses.every(status => status === 'healthy')) return 'Healthy'
  if (statuses.some(status => status === 'error' || status === 'unhealthy')) return 'Error'
  return 'Warning'
})

const overallStatusClass = computed(() => {
  switch (overallStatus.value) {
    case 'Healthy': return 'bg-green-100 text-green-800'
    case 'Error': return 'bg-red-100 text-red-800'
    default: return 'bg-yellow-100 text-yellow-800'
  }
})

const getStatusClass = (status?: string) => {
  switch (status) {
    case 'healthy': return 'bg-green-100 text-green-800'
    case 'error':
    case 'unhealthy': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const checkHealth = async () => {
  isLoading.value = true
  try {
    // Check overall health first - now that routing is fixed, this should work
    const response = await fetch('https://memo.myisland.dev/health')
    
    const responseText = await response.text()
    
    let overallData
    try {
      overallData = JSON.parse(responseText)
    } catch (parseError) {
      console.error('Failed to parse JSON:', parseError)
      return
    }
    
    // Extract service statuses from the services object
    if (overallData.services) {
      healthData.value = {
        database: { status: overallData.services.database || 'unknown' },
        config: { status: overallData.services.configuration || 'unknown' },
        llm: { status: overallData.services.llm || 'unknown' },
        auth: { status: overallData.services.auth || 'unknown' }
      }
    }
    
    // If we have detailed information, add it without overwriting status
    if (overallData.database_details && healthData.value.database) {
      healthData.value.database = {
        ...healthData.value.database,
        details: `Tables: ${overallData.database_details.tables?.length || 0}, Users: ${overallData.database_details.user_count || 0}`
      }
    }
    
    if (overallData.config_details && healthData.value.config) {
      healthData.value.config = {
        ...healthData.value.config,
        details: `Configs: ${overallData.config_details.configs_loaded?.length || 0}`
      }
    }
    
    if (overallData.llm_details && healthData.value.llm) {
      healthData.value.llm = {
        ...healthData.value.llm,
        details: `Provider: ${overallData.llm_details.provider}, Model: ${overallData.llm_details.model}`
      }
    }
    
    if (overallData.auth_details && healthData.value.auth) {
      healthData.value.auth = {
        ...healthData.value.auth,
        details: `Active Sessions: ${overallData.auth_details.active_sessions || 0}`
      }
    }
    
    lastUpdated.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('Failed to check health status:', error)
    // Set all services to unknown if the main health check fails
    healthData.value = {
      database: { status: 'unknown' },
      config: { status: 'unknown' },
      llm: { status: 'unknown' },
      auth: { status: 'unknown' }
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  checkHealth()
})
</script>
