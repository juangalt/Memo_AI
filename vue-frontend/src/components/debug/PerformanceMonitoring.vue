<template>
  <div class="space-y-4">
    <!-- Performance Metrics -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Performance Metrics</h5>
      <div class="grid grid-cols-2 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold text-blue-600">{{ avgResponseTime }}ms</div>
          <div class="text-sm text-gray-600">Avg Response Time</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ totalRequests }}</div>
          <div class="text-sm text-gray-600">Total Requests</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-purple-600">{{ successRate }}%</div>
          <div class="text-sm text-gray-600">Success Rate</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-orange-600">{{ errorRate }}%</div>
          <div class="text-sm text-gray-600">Error Rate</div>
        </div>
      </div>
    </div>
    
    <!-- Response Time Chart -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Response Time History</h5>
      <div class="h-32 bg-gray-50 rounded flex items-end justify-between p-2">
        <div
          v-for="(time, index) in responseTimeHistory"
          :key="index"
          :style="{ height: `${(time / maxResponseTime) * 100}%` }"
          :class="getResponseTimeClass(time)"
          class="w-4 rounded-t transition-all duration-300"
        ></div>
      </div>
      <div class="flex justify-between text-xs text-gray-500 mt-2">
        <span>0ms</span>
        <span>{{ maxResponseTime }}ms</span>
      </div>
    </div>
    
    <!-- Endpoint Performance -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Endpoint Performance</h5>
      <div class="space-y-2">
        <div
          v-for="endpoint in endpointPerformance"
          :key="endpoint.path"
          class="flex items-center justify-between p-2 bg-gray-50 rounded"
        >
          <div class="flex items-center space-x-2">
            <span class="text-sm font-mono">{{ endpoint.method }}</span>
            <span class="text-sm text-gray-700">{{ endpoint.path }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-sm font-mono">{{ endpoint.avgTime }}ms</span>
            <span :class="getStatusClass(endpoint.status)" class="px-2 py-1 rounded text-xs">
              {{ endpoint.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- System Resources -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">System Resources</h5>
      <div class="space-y-3">
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-600">Memory Usage</span>
            <span class="text-gray-900">{{ memoryUsage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :style="{ width: memoryUsage + '%' }"
              :class="getResourceClass(memoryUsage)"
              class="h-2 rounded-full transition-all duration-300"
            ></div>
          </div>
        </div>
        
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-600">CPU Usage</span>
            <span class="text-gray-900">{{ cpuUsage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :style="{ width: cpuUsage + '%' }"
              :class="getResourceClass(cpuUsage)"
              class="h-2 rounded-full transition-all duration-300"
            ></div>
          </div>
        </div>
        
        <div>
          <div class="flex justify-between text-sm mb-1">
            <span class="text-gray-600">Disk Usage</span>
            <span class="text-gray-900">{{ diskUsage }}%</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :style="{ width: diskUsage + '%' }"
              :class="getResourceClass(diskUsage)"
              class="h-2 rounded-full transition-all duration-300"
            ></div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Performance Controls -->
    <div class="bg-white rounded-lg border p-4">
      <h5 class="font-medium text-gray-900 mb-3">Performance Controls</h5>
      <div class="space-y-3">
        <button
          @click="startMonitoring"
          :disabled="isMonitoring"
          class="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {{ isMonitoring ? 'Monitoring...' : 'Start Monitoring' }}
        </button>
        
        <button
          @click="clearMetrics"
          class="w-full px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Clear Metrics
        </button>
      </div>
    </div>
    
    <!-- Last Updated -->
    <div class="text-xs text-gray-500 text-center">
      Last updated: {{ lastUpdated }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface EndpointPerformance {
  method: string
  path: string
  avgTime: number
  status: string
}

const isMonitoring = ref(false)
const responseTimeHistory = ref<number[]>([])
const endpointPerformance = ref<EndpointPerformance[]>([])
const memoryUsage = ref(45)
const cpuUsage = ref(32)
const diskUsage = ref(28)
const totalRequests = ref(0)
const successfulRequests = ref(0)
const failedRequests = ref(0)
const lastUpdated = ref('Never')
const monitoringInterval = ref<number | null>(null)

const avgResponseTime = computed(() => {
  if (responseTimeHistory.value.length === 0) return 0
  const sum = responseTimeHistory.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / responseTimeHistory.value.length)
})

const maxResponseTime = computed(() => {
  if (responseTimeHistory.value.length === 0) return 1000
  return Math.max(...responseTimeHistory.value, 1000)
})

const successRate = computed(() => {
  if (totalRequests.value === 0) return 100
  return Math.round((successfulRequests.value / totalRequests.value) * 100)
})

const errorRate = computed(() => {
  if (totalRequests.value === 0) return 0
  return Math.round((failedRequests.value / totalRequests.value) * 100)
})

const getResponseTimeClass = (time: number) => {
  if (time < 100) return 'bg-green-500'
  if (time < 500) return 'bg-yellow-500'
  return 'bg-red-500'
}

const getStatusClass = (status: string) => {
  if (status === 'ok') return 'bg-green-100 text-green-800'
  if (status === 'error') return 'bg-red-100 text-red-800'
  return 'bg-yellow-100 text-yellow-800'
}

const getResourceClass = (usage: number) => {
  if (usage < 50) return 'bg-green-500'
  if (usage < 80) return 'bg-yellow-500'
  return 'bg-red-500'
}

const startMonitoring = () => {
  isMonitoring.value = true
  
  // Simulate performance monitoring
  monitoringInterval.value = window.setInterval(() => {
    // Simulate response time data
    const newResponseTime = Math.random() * 500 + 50
    responseTimeHistory.value.push(newResponseTime)
    
    // Keep only last 20 measurements
    if (responseTimeHistory.value.length > 20) {
      responseTimeHistory.value = responseTimeHistory.value.slice(-20)
    }
    
    // Simulate endpoint performance
    endpointPerformance.value = [
      { method: 'GET', path: '/health', avgTime: Math.round(Math.random() * 50 + 10), status: 'ok' },
      { method: 'POST', path: '/api/v1/evaluations/submit', avgTime: Math.round(Math.random() * 200 + 100), status: 'ok' },
      { method: 'GET', path: '/api/v1/auth/validate', avgTime: Math.round(Math.random() * 30 + 5), status: 'ok' }
    ]
    
    // Simulate system resources
    memoryUsage.value = Math.round(Math.random() * 30 + 40)
    cpuUsage.value = Math.round(Math.random() * 40 + 20)
    diskUsage.value = Math.round(Math.random() * 20 + 20)
    
    // Update request counts
    totalRequests.value += Math.round(Math.random() * 5 + 1)
    successfulRequests.value += Math.round(Math.random() * 4 + 1)
    failedRequests.value = totalRequests.value - successfulRequests.value
    
    lastUpdated.value = new Date().toLocaleTimeString()
  }, 2000)
}

const clearMetrics = () => {
  responseTimeHistory.value = []
  endpointPerformance.value = []
  totalRequests.value = 0
  successfulRequests.value = 0
  failedRequests.value = 0
  lastUpdated.value = 'Never'
}

onMounted(() => {
  startMonitoring()
})

onUnmounted(() => {
  if (monitoringInterval.value) {
    clearInterval(monitoringInterval.value)
  }
})
</script>

