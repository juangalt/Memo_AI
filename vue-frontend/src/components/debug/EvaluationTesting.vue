<template>
  <div class="space-y-4">
    <div class="bg-white rounded-lg border p-4">
      <div class="flex items-center justify-between mb-4">
        <h5 class="font-medium text-gray-900">Evaluation Endpoint Testing</h5>
        <button 
          @click="runEvaluationTest" 
          :disabled="isTesting" 
          class="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isTesting ? 'Testing...' : 'Test Evaluation' }}
        </button>
      </div>
      
      <div class="text-xs text-gray-600 mb-4">
        <p>⚠️ <strong>Note:</strong> This test uses LLM processing and may take 5-15 seconds to complete.</p>
        <p>⚠️ <strong>Authentication Required:</strong> You must be logged in to test this endpoint.</p>
      </div>

      <div v-if="testResult" class="border rounded-lg p-3" :class="getResultStatusClass(testResult.status)">
        <!-- Header Row -->
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-mono px-2 py-1 rounded bg-gray-100">POST</span>
            <span class="text-sm font-medium text-gray-900">Submit Evaluation</span>
          </div>
          <div class="flex items-center space-x-2">
            <div v-if="testResult.status === 'testing'" class="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
            <span v-else :class="getStatusBadgeClass(testResult.status)" class="px-2 py-1 rounded-full text-xs font-medium">
              {{ getStatusText(testResult.status) }}
            </span>
            <span v-if="testResult.responseTime" class="text-xs text-gray-500">
              {{ testResult.responseTime }}ms
            </span>
          </div>
        </div>
        
        <!-- Path -->
        <div class="text-xs text-gray-500 break-all mb-2">/api/v1/evaluations/submit</div>
        
        <!-- Response Preview -->
        <div v-if="testResult.response && testResult.status === 'healthy'" class="relative group mb-2">
          <div class="text-xs text-green-600 bg-green-50 p-2 rounded break-words cursor-help" :title="testResult.response">
            <div class="flex items-center justify-between">
              <span class="truncate">Response: {{ getResponsePreview(testResult.response) }}</span>
              <span class="text-green-500 ml-2 flex-shrink-0">👁️</span>
            </div>
          </div>
          <div class="absolute bottom-full left-0 right-0 mb-2 bg-gray-900 text-white text-xs rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 max-w-sm max-h-32 overflow-y-auto">
            <div class="break-words font-mono">{{ testResult.response }}</div>
            <div class="text-gray-400 mt-1">Response preview</div>
            <div class="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
        
        <!-- Error Details with Tooltip -->
        <div v-if="testResult.error" class="relative group">
          <div class="text-xs text-red-600 bg-red-50 p-2 rounded break-words cursor-pointer hover:bg-red-100 transition-colors" 
               @click="copyToClipboard(testResult)" 
               :title="getDebugErrorInfo(testResult)">
            <div class="flex items-center justify-between">
              <span class="truncate">{{ testResult.error }}</span>
              <span class="text-red-500 ml-2 flex-shrink-0">📋</span>
            </div>
          </div>
          <div class="absolute bottom-full left-0 right-0 mb-2 bg-gray-900 text-white text-xs rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10 max-w-sm max-h-64 overflow-y-auto">
            <div class="break-words font-mono whitespace-pre-line">{{ getDebugErrorInfo(testResult) }}</div>
            <div class="text-gray-400 mt-2 text-center">Click to copy full debug info to clipboard</div>
            <div class="absolute top-full left-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      </div>

      <div v-else class="text-xs text-gray-500 text-center py-4">
        Click "Test Evaluation" to run the evaluation endpoint test
      </div>
    </div>
    
    <!-- Last Test Time -->
    <div v-if="lastTested" class="text-xs text-gray-500 text-center">Last tested: {{ lastTested }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { apiClient } from '@/services/api'

interface TestResult {
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
const lastTested = ref('')
const testResult = ref<TestResult | null>(null)

const getResultStatusClass = (status: string) => {
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

const getResponsePreview = (response: string) => {
  const maxLength = 100
  if (response.length <= maxLength) return response
  return response.substring(0, maxLength) + '...'
}

const getDebugErrorInfo = (result: TestResult) => {
  const baseUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
  const fullUrl = `${baseUrl}/api/v1/evaluations/submit`
  
  return `=== EVALUATION ENDPOINT ERROR DEBUG INFO ===

Endpoint: Submit Evaluation
Method: POST
Path: /api/v1/evaluations/submit
Full URL: ${fullUrl}
Status Code: ${result.statusCode || 'Unknown'}
Response Time: ${result.responseTime || 'N/A'}ms
Timestamp: ${result.timestamp || new Date().toISOString()}
Requires Authentication: Yes

Error Message: ${result.error}

Request Data: ${result.requestData ? JSON.stringify(result.requestData, null, 2) : 'N/A'}

Response Data: ${result.responseData ? JSON.stringify(result.responseData, null, 2) : 'N/A'}

Environment:
- Backend URL: ${baseUrl}
- User Agent: ${navigator.userAgent}
- Timestamp: ${new Date().toISOString()}

Notes:
- This endpoint requires authentication (X-Session-Token header)
- Evaluation endpoint requires valid text_content in request body
- LLM processing may take 5-15 seconds to complete
- Test uses sample memo text for evaluation

=== END DEBUG INFO ===`
}

const copyToClipboard = async (result: TestResult) => {
  try {
    const debugInfo = getDebugErrorInfo(result)
    await navigator.clipboard.writeText(debugInfo)
    console.log('Debug info copied to clipboard:', debugInfo)
  } catch (err) {
    console.error('Failed to copy debug info to clipboard:', err)
  }
}

const runEvaluationTest = async () => {
  isTesting.value = true
  testResult.value = {
    status: 'testing',
    error: undefined,
    response: undefined,
    responseTime: undefined,
    statusCode: undefined,
    requestData: undefined,
    responseData: undefined,
    timestamp: undefined
  }
  
  const startTime = Date.now()
  const timestamp = new Date().toISOString()
  
  try {
    const requestData = {
      text_content: "This is a sample memo for testing purposes. It contains some basic content to evaluate the system's functionality and demonstrates the evaluation capabilities of the Memo AI Coach application."
    }
    
    const result = await apiClient.post('/api/v1/evaluations/submit', requestData)
    const responseTime = Date.now() - startTime
    
    if (result.success) {
      testResult.value = {
        status: 'healthy',
        responseTime: responseTime,
        response: JSON.stringify(result.data, null, 2),
        statusCode: 200,
        requestData: requestData,
        responseData: result.data,
        timestamp: timestamp
      }
    } else {
      testResult.value = {
        status: 'error',
        error: result.error || 'Request failed',
        responseTime: responseTime,
        statusCode: result.status || 400,
        requestData: requestData,
        responseData: result.data || result,
        timestamp: timestamp
      }
    }
  } catch (error) {
    const responseTime = Date.now() - startTime
    testResult.value = {
      status: 'error',
      error: (error as Error).message,
      responseTime: responseTime,
      statusCode: 500,
      requestData: { method: 'POST', path: '/api/v1/evaluations/submit' },
      responseData: undefined,
      timestamp: timestamp
    }
  }
  
  isTesting.value = false
  lastTested.value = new Date().toLocaleTimeString()
}
</script>
