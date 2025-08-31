<template>
  <div class="space-y-4">
    <!-- API Endpoints Health Status -->
    <div class="bg-white rounded-lg border p-4">
      <div class="flex items-center justify-between mb-4">
        <h5 class="font-medium text-gray-900">API Endpoints Health</h5>
        <button
          @click="runAllTests"
          :disabled="isTesting"
          class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isTesting ? 'Testing...' : 'Test All Endpoints' }}
        </button>
      </div>
      
      <!-- Endpoints Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="endpoint in endpoints"
          :key="endpoint.path"
          class="border rounded-lg p-3 min-h-[80px]"
          :class="getEndpointStatusClass(endpoint.status)"
        >
          <!-- Header Row -->
          <div class="flex items-center justify-between mb-2">
            <div class="flex items-center space-x-2 flex-1 min-w-0">
              <span class="text-xs font-mono px-2 py-1 rounded bg-gray-100 flex-shrink-0">
                {{ endpoint.method }}
              </span>
              <span class="text-sm font-medium text-gray-900 truncate">
                {{ endpoint.name }}
              </span>
            </div>
          </div>
          
          <!-- Status and Response Time Row -->
          <div class="flex items-center justify-end mb-2">
            <div class="flex items-center space-x-2">
              <div
                v-if="endpoint.status === 'testing'"
                class="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"
              ></div>
              <span
                v-else
                :class="getStatusBadgeClass(endpoint.status)"
                class="px-2 py-1 rounded-full text-xs font-medium whitespace-nowrap"
              >
                {{ getStatusText(endpoint.status) }}
              </span>
              <span
                v-if="endpoint.responseTime"
                class="text-xs text-gray-500 whitespace-nowrap"
              >
                {{ endpoint.responseTime }}ms
              </span>
            </div>
          </div>
          
          <!-- Error Details with Tooltip -->
          <div
            v-if="endpoint.error"
            class="mt-2 relative group"
          >
            <div class="text-xs text-red-600 bg-red-50 p-2 rounded break-words cursor-pointer hover:bg-red-100 transition-colors"
                 @click="copyToClipboard(endpoint)"
                 :title="getDebugErrorInfo(endpoint)">
              <div class="flex items-center justify-between">
                <span class="truncate">{{ endpoint.error }}</span>
                <span class="text-red-500 ml-2 flex-shrink-0">📋</span>
              </div>
            </div>
            
            <!-- Tooltip -->
            <div class="absolute bottom-full left-0 right-0 mb-2 bg-gray-900 text-white text-xs rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 max-w-sm max-h-64 overflow-y-auto">
              <div class="break-words font-mono whitespace-pre-line">{{ getDebugErrorInfo(endpoint) }}</div>
              <div class="text-gray-400 mt-2 text-center">Click to copy full debug info to clipboard</div>
              <!-- Arrow -->
              <div class="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
          
          <!-- Response Details with Tooltip -->
          <div
            v-if="endpoint.response && endpoint.status === 'healthy'"
            class="mt-2 relative group"
          >
            <div class="text-xs text-green-600 bg-green-50 p-2 rounded break-words cursor-help"
                 :title="endpoint.response">
              <div class="flex items-center justify-between">
                <span class="truncate">Response: {{ getResponsePreview(endpoint.response) }}</span>
                <span class="text-green-500 ml-2 flex-shrink-0">👁️</span>
              </div>
            </div>
            
            <!-- Tooltip -->
            <div class="absolute bottom-full left-0 right-0 mb-2 bg-gray-900 text-white text-xs rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 max-w-sm max-h-32 overflow-y-auto">
              <div class="break-words font-mono">{{ endpoint.response }}</div>
              <div class="text-gray-400 mt-1">Response preview</div>
              <!-- Arrow -->
              <div class="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Summary -->
    <div class="bg-white rounded-lg border p-4">
      <div class="flex items-center justify-between">
        <span class="font-medium text-gray-900">Health Summary</span>
        <span :class="getSummaryClass()" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ getSummaryText() }}
        </span>
      </div>
      <div class="text-xs text-gray-600 mt-1">
        {{ healthyCount }} healthy, {{ errorCount }} errors, {{ testingCount }} testing
      </div>
    </div>
    
    <!-- Last Test Time -->
    <div class="text-xs text-gray-500 text-center">
      Last tested: {{ lastTested }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/services/api'

interface Endpoint {
  name: string
  method: string
  path: string
  description: string
  status: 'unknown' | 'healthy' | 'error' | 'testing'
  responseTime?: number
  error?: string
  response?: string
  statusCode?: number
  requestData?: any
  responseData?: any
  timestamp?: string
}

const isTesting = ref(false)
const lastTested = ref('Never')

const endpoints = ref<Endpoint[]>([
  // Health endpoints
  { name: 'System Health', method: 'GET', path: '/health', description: 'Overall system health', status: 'unknown' },
  { name: 'Database Health', method: 'GET', path: '/health/database', description: 'Database health check', status: 'unknown' },
  { name: 'Config Health', method: 'GET', path: '/health/config', description: 'Configuration health check', status: 'unknown' },
  { name: 'LLM Health', method: 'GET', path: '/health/llm', description: 'LLM service health check', status: 'unknown' },
  { name: 'Auth Health', method: 'GET', path: '/health/auth', description: 'Authentication service health check', status: 'unknown' },
  
  // API endpoints
  { name: 'Auth Validate', method: 'GET', path: '/api/v1/auth/validate', description: 'Validate session', status: 'unknown' },
  { name: 'List Users', method: 'GET', path: '/api/v1/admin/users', description: 'List all users', status: 'unknown' },
  
  // Config endpoints
  { name: 'Config: Rubric', method: 'GET', path: '/api/v1/admin/config/rubric', description: 'Get rubric configuration', status: 'unknown' },
  { name: 'Config: Prompt', method: 'GET', path: '/api/v1/admin/config/prompt', description: 'Get prompt configuration', status: 'unknown' },
  { name: 'Config: Auth', method: 'GET', path: '/api/v1/admin/config/auth', description: 'Get auth configuration', status: 'unknown' },
  { name: 'Config: LLM', method: 'GET', path: '/api/v1/admin/config/llm', description: 'Get LLM configuration', status: 'unknown' },
  
  // Evaluation endpoints
  { name: 'Submit Evaluation', method: 'POST', path: '/api/v1/evaluations/submit', description: 'Submit text for evaluation', status: 'unknown' }
])

const healthyCount = computed(() => endpoints.value.filter(e => e.status === 'healthy').length)
const errorCount = computed(() => endpoints.value.filter(e => e.status === 'error').length)
const testingCount = computed(() => endpoints.value.filter(e => e.status === 'testing').length)

const getEndpointStatusClass = (status: string) => {
  switch (status) {
    case 'healthy': return 'border-green-200 bg-green-50'
    case 'error': return 'border-red-200 bg-red-50'
    case 'testing': return 'border-blue-200 bg-blue-50'
    default: return 'border-gray-200 bg-gray-50'
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'healthy': return 'bg-green-100 text-green-800'
    case 'error': return 'bg-red-100 text-red-800'
    case 'testing': return 'bg-blue-100 text-blue-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'healthy': return 'Healthy'
    case 'error': return 'Error'
    case 'testing': return 'Testing'
    default: return 'Unknown'
  }
}

const getSummaryClass = () => {
  if (errorCount.value > 0) return 'bg-red-100 text-red-800'
  if (testingCount.value > 0) return 'bg-blue-100 text-blue-800'
  if (healthyCount.value === endpoints.value.length) return 'bg-green-100 text-green-800'
  return 'bg-gray-100 text-gray-800'
}

const getSummaryText = () => {
  if (errorCount.value > 0) return `${errorCount.value} Errors`
  if (testingCount.value > 0) return 'Testing'
  if (healthyCount.value === endpoints.value.length) return 'All Healthy'
  return 'Unknown'
}

const getResponsePreview = (response: string) => {
  if (!response) return ''
  const maxLength = 50
  return response.length > maxLength ? response.substring(0, maxLength) + '...' : response
}

const getDebugErrorInfo = (endpoint: Endpoint) => {
  const baseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
  const fullUrl = `${baseUrl}${endpoint.path}`
  
  // Determine if endpoint requires authentication
  const requiresAuth = endpoint.path.includes('/api/v1/evaluations/') || 
                      endpoint.path.includes('/api/v1/admin/') ||
                      endpoint.path.includes('/api/v1/sessions/')
  
  return `=== API ENDPOINT ERROR DEBUG INFO ===

Endpoint: ${endpoint.name}
Method: ${endpoint.method}
Path: ${endpoint.path}
Full URL: ${fullUrl}
Status Code: ${endpoint.statusCode || 'Unknown'}
Response Time: ${endpoint.responseTime || 'N/A'}ms
Timestamp: ${endpoint.timestamp || new Date().toISOString()}
Requires Authentication: ${requiresAuth ? 'Yes' : 'No'}

Error Message: ${endpoint.error}

Request Data: ${endpoint.requestData ? JSON.stringify(endpoint.requestData, null, 2) : 'N/A'}

Response Data: ${endpoint.responseData ? JSON.stringify(endpoint.responseData, null, 2) : 'N/A'}

Environment:
- Backend URL: ${baseUrl}
- User Agent: ${navigator.userAgent}
- Timestamp: ${new Date().toISOString()}

Notes:
${requiresAuth ? '- This endpoint requires authentication (X-Session-Token header)' : '- This is a public endpoint'}
${endpoint.path === '/api/v1/evaluations/submit' ? '- Evaluation endpoint requires valid text_content in request body' : ''}
${endpoint.path.includes('/api/v1/admin/') ? '- Admin endpoint requires admin privileges' : ''}

=== END DEBUG INFO ===`
}

const copyToClipboard = async (endpoint: Endpoint) => {
  try {
    const debugInfo = getDebugErrorInfo(endpoint)
    await navigator.clipboard.writeText(debugInfo)
    console.log('Debug info copied to clipboard:', debugInfo)
  } catch (err) {
    console.error('Failed to copy debug info to clipboard:', err)
  }
}

const testEndpoint = async (endpoint: Endpoint) => {
  endpoint.status = 'testing'
  endpoint.error = undefined
  endpoint.response = undefined
  endpoint.responseTime = undefined
  endpoint.statusCode = undefined
  endpoint.requestData = undefined
  endpoint.responseData = undefined
  endpoint.timestamp = undefined
  
  const startTime = Date.now()
  const timestamp = new Date().toISOString()
  
  try {
    let result: any
    let requestData: any = undefined
    
    // Prepare appropriate test data based on endpoint
    if (endpoint.path === '/api/v1/evaluations/submit') {
      requestData = {
        text_content: "This is a sample memo for testing purposes. It contains some basic content to evaluate the system's functionality."
      }
    } else if (endpoint.method === 'POST') {
      requestData = { test: true }
    }
    
    switch (endpoint.method) {
      case 'GET':
        result = await apiClient.get(endpoint.path)
        break
      case 'POST':
        result = await apiClient.post(endpoint.path, requestData)
        break
      default:
        throw new Error(`Unsupported method: ${endpoint.method}`)
    }
    
    const responseTime = Date.now() - startTime
    
    if (result.success) {
      endpoint.status = 'healthy'
      endpoint.responseTime = responseTime
      endpoint.response = JSON.stringify(result.data, null, 2)
      endpoint.statusCode = 200
      endpoint.requestData = requestData
      endpoint.responseData = result.data
      endpoint.timestamp = timestamp
    } else {
      endpoint.status = 'error'
      endpoint.error = result.error || 'Request failed'
      endpoint.responseTime = responseTime
      endpoint.statusCode = result.status || 400
      endpoint.requestData = requestData
      endpoint.responseData = result.data || result
      endpoint.timestamp = timestamp
    }
  } catch (error) {
    const responseTime = Date.now() - startTime
    endpoint.status = 'error'
    endpoint.error = (error as Error).message
    endpoint.responseTime = responseTime
    endpoint.statusCode = 500 // Generic error status code
    endpoint.requestData = { method: endpoint.method, path: endpoint.path }
    endpoint.responseData = undefined
    endpoint.timestamp = timestamp
  }
}

const runAllTests = async () => {
  isTesting.value = true
  
  // Reset all endpoints to unknown
  endpoints.value.forEach(endpoint => {
    endpoint.status = 'unknown'
    endpoint.error = undefined
    endpoint.response = undefined
    endpoint.responseTime = undefined
    endpoint.statusCode = undefined
    endpoint.requestData = undefined
    endpoint.responseData = undefined
    endpoint.timestamp = undefined
  })
  
  // Test all endpoints concurrently
  const testPromises = endpoints.value.map(endpoint => testEndpoint(endpoint))
  await Promise.all(testPromises)
  
  isTesting.value = false
  lastTested.value = new Date().toLocaleTimeString()
}

onMounted(() => {
  // Run initial test
  runAllTests()
})
</script>
