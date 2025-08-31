<template>
  <div class="space-y-4">
    <!-- API Test Form -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">API Endpoint Testing</h5>
      <form @submit.prevent="testEndpoint" class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <select
            v-model="selectedEndpoint"
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select endpoint...</option>
            <option v-for="endpoint in endpoints" :key="endpoint.path" :value="endpoint.path">
              {{ endpoint.method }} {{ endpoint.path }}
            </option>
          </select>
          <button
            type="submit"
            :disabled="isTesting"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ isTesting ? 'Testing...' : 'Test Endpoint' }}
          </button>
        </div>
        
        <!-- Custom Endpoint -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
          <select
            v-model="customMethod"
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
          </select>
          <input
            v-model="customPath"
            type="text"
            placeholder="/api/v1/..."
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            @click="testCustomEndpoint"
            :disabled="isTesting || !customPath"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            Test Custom
          </button>
        </div>
      </form>
    </div>
    
    <!-- Request/Response Display -->
    <div v-if="testResult" class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Test Results</h5>
      
      <!-- Request Info -->
      <div class="mb-4">
        <h6 class="font-medium text-gray-700 mb-2">Request</h6>
        <div class="bg-gray-100 rounded p-3 text-sm">
          <div class="flex items-center space-x-2 mb-2">
            <span class="font-mono text-blue-600">{{ testResult.method }}</span>
            <span class="font-mono text-gray-800">{{ testResult.url }}</span>
          </div>
          <div v-if="testResult.requestBody" class="mt-2">
            <span class="text-gray-600">Body:</span>
            <pre class="text-xs bg-white p-2 rounded mt-1 overflow-x-auto">{{ JSON.stringify(testResult.requestBody, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- Response Info -->
      <div class="mb-4">
        <h6 class="font-medium text-gray-700 mb-2">Response</h6>
        <div class="bg-gray-100 rounded p-3 text-sm">
          <div class="flex items-center space-x-2 mb-2">
            <span :class="getStatusClass(testResult.status)" class="px-2 py-1 rounded text-xs font-medium">
              {{ testResult.status }}
            </span>
            <span class="text-gray-600">{{ testResult.responseTime }}ms</span>
          </div>
          <div v-if="testResult.responseBody" class="mt-2">
            <span class="text-gray-600">Body:</span>
            <pre class="text-xs bg-white p-2 rounded mt-1 overflow-x-auto max-h-64 overflow-y-auto">{{ JSON.stringify(testResult.responseBody, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- Error Info -->
      <div v-if="testResult.error" class="mb-4">
        <h6 class="font-medium text-red-700 mb-2">Error</h6>
        <div class="bg-red-50 border border-red-200 rounded p-3 text-sm">
          <div class="text-red-800">{{ testResult.error }}</div>
        </div>
      </div>
    </div>
    
    <!-- Quick Test Buttons -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Quick Tests</h5>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="quickTest in quickTests"
          :key="quickTest.name"
          @click="runQuickTest(quickTest)"
          :disabled="isTesting"
          class="px-3 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
        >
          {{ quickTest.name }}
        </button>
      </div>
    </div>
    
    <!-- Test History -->
    <div v-if="testHistory.length > 0" class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Test History</h5>
      <div class="space-y-2 max-h-32 overflow-y-auto">
        <div
          v-for="test in testHistory"
          :key="test.id"
          class="flex items-center justify-between text-sm p-2 bg-gray-50 rounded"
        >
          <div class="flex items-center space-x-2">
            <span :class="getStatusClass(test.status)" class="px-2 py-1 rounded text-xs">
              {{ test.status }}
            </span>
            <span class="font-mono">{{ test.method }} {{ test.path }}</span>
          </div>
          <span class="text-xs text-gray-500">{{ test.timestamp }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '@/services/api'

interface Endpoint {
  method: string
  path: string
  description: string
}

interface TestResult {
  method: string
  url: string
  status: number
  responseTime: number
  responseBody: any
  requestBody?: any
  error?: string
}

interface TestHistoryItem {
  id: string
  method: string
  path: string
  status: number
  timestamp: string
}

const isTesting = ref(false)
const selectedEndpoint = ref('')
const customMethod = ref('GET')
const customPath = ref('')
const testResult = ref<TestResult | null>(null)
const testHistory = ref<TestHistoryItem[]>([])

const endpoints: Endpoint[] = [
  { method: 'GET', path: '/health', description: 'System health check' },
  { method: 'GET', path: '/api/v1/auth/validate', description: 'Validate session' },
  { method: 'GET', path: '/api/v1/admin/users', description: 'List users' },
  { method: 'GET', path: '/api/v1/admin/config/rubric', description: 'Get rubric configuration' },
  { method: 'GET', path: '/api/v1/admin/config/prompt', description: 'Get prompt configuration' },
  { method: 'GET', path: '/api/v1/admin/config/auth', description: 'Get auth configuration' },
  { method: 'GET', path: '/api/v1/admin/config/llm', description: 'Get LLM configuration' },
  { method: 'POST', path: '/api/v1/evaluations/submit', description: 'Submit evaluation' }
]

const quickTests = [
  { name: 'Health Check', method: 'GET', path: '/health' },
  { name: 'Auth Validate', method: 'GET', path: '/api/v1/auth/validate' },
  { name: 'List Users', method: 'GET', path: '/api/v1/admin/users' },
  { name: 'Config: Rubric', method: 'GET', path: '/api/v1/admin/config/rubric' },
  { name: 'Config: Prompt', method: 'GET', path: '/api/v1/admin/config/prompt' },
  { name: 'Config: Auth', method: 'GET', path: '/api/v1/admin/config/auth' },
  { name: 'Config: LLM', method: 'GET', path: '/api/v1/admin/config/llm' }
]

const getStatusClass = (status: number) => {
  if (status >= 200 && status < 300) return 'bg-green-100 text-green-800'
  if (status >= 400 && status < 500) return 'bg-yellow-100 text-yellow-800'
  if (status >= 500) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

const testEndpoint = async () => {
  if (!selectedEndpoint.value) return
  
  const endpoint = endpoints.find(e => e.path === selectedEndpoint.value)
  if (!endpoint) return
  
  await performTest(endpoint.method, endpoint.path)
}

const testCustomEndpoint = async () => {
  if (!customPath.value) return
  await performTest(customMethod.value, customPath.value)
}

const runQuickTest = async (test: { name: string; method: string; path: string }) => {
  await performTest(test.method, test.path)
}

const performTest = async (method: string, path: string) => {
  isTesting.value = true
  const startTime = Date.now()
  
  try {
    let result: any
    
    switch (method) {
      case 'GET':
        result = await apiClient.get(path)
        break
      case 'POST':
        result = await apiClient.post(path, { test: true })
        break
      case 'PUT':
        result = await apiClient.put(path, { test: true })
        break
      case 'DELETE':
        result = await apiClient.delete(path)
        break
      default:
        throw new Error(`Unsupported method: ${method}`)
    }
    
    const responseTime = Date.now() - startTime
    
    testResult.value = {
      method,
      url: path,
      status: result.status || 200,
      responseTime,
      responseBody: result.data,
      requestBody: method !== 'GET' ? { test: true } : undefined
    }
    
    // Add to history
    testHistory.value.unshift({
      id: Date.now().toString(),
      method,
      path,
      status: result.status || 200,
      timestamp: new Date().toLocaleTimeString()
    })
    
    // Keep only last 10 tests
    if (testHistory.value.length > 10) {
      testHistory.value = testHistory.value.slice(0, 10)
    }
    
  } catch (error) {
    const responseTime = Date.now() - startTime
    
    testResult.value = {
      method,
      url: path,
      status: (error as any).status || 500,
      responseTime,
      responseBody: null,
      error: (error as Error).message
    }
    
    // Add to history
    testHistory.value.unshift({
      id: Date.now().toString(),
      method,
      path,
      status: (error as any).status || 500,
      timestamp: new Date().toLocaleTimeString()
    })
  } finally {
    isTesting.value = false
  }
}
</script>

