<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          📜 Admin Logs
        </h1>

        <!-- Summary / Controls -->
        <div class="bg-gray-50 rounded-lg p-4 sm:p-6 border border-gray-200 mb-6">
          <div class="flex flex-col gap-3">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div class="text-sm text-gray-700">
                <span class="font-medium">Shown:</span>
                <span class="ml-1">{{ filteredLogs.length }}</span>
                <span class="ml-2 text-gray-500">of {{ logs.length }}</span>
                <span v-if="sourceLabel" class="ml-2 px-2 py-0.5 text-xs rounded bg-blue-100 text-blue-800">{{ sourceLabel }}</span>
              </div>
              <div class="flex items-center gap-2">
                <button @click="refresh" class="px-3 py-2 bg-blue-600 text-white rounded text-xs sm:text-sm hover:bg-blue-700">Refresh</button>
              </div>
            </div>
            <div class="flex items-center flex-wrap gap-3">
              <span class="text-xs sm:text-sm text-gray-600">Levels:</span>
              <label class="inline-flex items-center gap-1 text-xs sm:text-sm text-gray-700">
                <input type="checkbox" v-model="levelFilters.DEBUG" class="h-4 w-4" /> Debug
              </label>
              <label class="inline-flex items-center gap-1 text-xs sm:text-sm text-gray-700">
                <input type="checkbox" v-model="levelFilters.INFO" class="h-4 w-4" /> Info
              </label>
              <label class="inline-flex items-center gap-1 text-xs sm:text-sm text-gray-700">
                <input type="checkbox" v-model="levelFilters.WARNING" class="h-4 w-4" /> Warning
              </label>
              <label class="inline-flex items-center gap-1 text-xs sm:text-sm text-gray-700">
                <input type="checkbox" v-model="levelFilters.ERROR" class="h-4 w-4" /> Error
              </label>
              <label class="inline-flex items-center gap-1 text-xs sm:text-sm text-gray-700">
                <input type="checkbox" v-model="levelFilters.CRITICAL" class="h-4 w-4" /> Critical
              </label>
              <div class="ml-auto flex items-center gap-2">
                <button type="button" @click="setAllLevels(true)" class="px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300">All</button>
                <button type="button" @click="setAllLevels(false)" class="px-2 py-1 text-xs bg-gray-200 rounded hover:bg-gray-300">None</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Raw Console View -->
        <div v-if="!isLoading && filteredLogs.length" class="border rounded-lg overflow-hidden">
          <div class="bg-gray-800 text-gray-200 font-mono text-xs sm:text-sm p-3">
            Console Output
          </div>
          <div class="bg-black">
            <pre class="text-green-200 font-mono text-xs sm:text-sm whitespace-pre-wrap p-4 h-[60vh] overflow-auto">{{ rawAll }}</pre>
          </div>
        </div>

        <!-- Empty / Loading states -->
        <div v-if="isLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-sm text-gray-600 mt-2">Loading logs...</p>
        </div>

        <div v-else-if="!filteredLogs.length" class="text-center py-8">
          <div class="text-gray-500">
            <div class="text-4xl mb-4">🗂️</div>
            <p class="text-lg mb-2">No logs to display</p>
            <p class="text-sm">Try changing the filters or refreshing</p>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Layout from '@/components/Layout.vue'
import { apiClient } from '@/services/api'

interface LogEntry {
  timestamp: string | Date
  level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' | string
  message: string
  context?: string
  details?: string
}

// State
const isLoading = ref<boolean>(false)
const error = ref<string>('')
const logs = ref<LogEntry[]>([])
const levelFilters = ref<Record<'DEBUG'|'INFO'|'WARNING'|'ERROR'|'CRITICAL', boolean>>({
  DEBUG: true,
  INFO: true,
  WARNING: true,
  ERROR: true,
  CRITICAL: true
})
const sourceLabel = ref<string>('')

// Helpers
const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric', month: 'short', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

const levelPillClass = (level: string) => {
  switch (level) {
    case 'DEBUG': return 'bg-gray-200 text-gray-800'
    case 'INFO': return 'bg-blue-100 text-blue-800'
    case 'WARNING': return 'bg-yellow-100 text-yellow-800'
    case 'ERROR': return 'bg-red-100 text-red-800'
    case 'CRITICAL': return 'bg-purple-100 text-purple-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

// Build raw text block
const formatLine = (e: LogEntry) => {
  const ts = new Date(e.timestamp).toISOString()
  const logger = (e as any).logger || 'app'
  const context = e.context ? ` [${e.context}]` : ''
  const main = `${ts} - ${logger} - ${e.level} - ${e.message}${context}`
  if (e.details) return `${main}\n${e.details.trim()}`
  return main
}

// Filter and combine logs into a single console-style block (newest to oldest)
const filteredLogs = computed(() => {
  return logs.value.filter((e) => {
    const key = (e.level || 'INFO').toString().toUpperCase() as keyof typeof levelFilters.value
    const flag = (levelFilters.value as any)[key]
    return typeof flag === 'boolean' ? flag : true
  })
})

const rawAll = computed(() => {
  const sorted = [...filteredLogs.value].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
  return sorted.map(formatLine).join('\n')
})

const setAllLevels = (value: boolean) => {
  // Replace entire object to avoid any reactivity edge cases
  levelFilters.value = {
    DEBUG: value,
    INFO: value,
    WARNING: value,
    ERROR: value,
    CRITICAL: value
  }
}

const loadLogs = async () => {
  isLoading.value = true
  error.value = ''
  sourceLabel.value = ''
  try {
    // Attempt to fetch logs from admin API (if implemented)
    const res = await apiClient.get<{ logs: LogEntry[] }>(`/api/v1/admin/logs?limit=1000`)
    if (res.success && res.data && Array.isArray((res.data as any).logs)) {
      logs.value = (res.data as any).logs
      sourceLabel.value = 'API'
    } else {
      throw new Error('Logs endpoint unavailable')
    }
  } catch (e) {
    // Fallback mock data for development if backend endpoint not available
    logs.value = [
      {
        timestamp: new Date(),
        level: 'INFO',
        message: 'Server started and configuration loaded',
        context: 'Application initialization sequence completed successfully.'
      },
      {
        timestamp: new Date(),
        level: 'WARNING',
        message: 'High LLM latency detected',
        context: 'Average processing time exceeded threshold for /api/v1/evaluations/submit',
        details: 'Last 5 requests averaged 16.2s; target < 15s.'
      },
      {
        timestamp: new Date(),
        level: 'ERROR',
        message: 'Failed to read configuration file',
        context: 'config/prompt.yaml',
        details: 'YAML validation error at line 42: unexpected indent.'
      }
    ]
    sourceLabel.value = 'Mock'
  } finally {
    isLoading.value = false
  }
}

const refresh = async () => {
  await loadLogs()
}

onMounted(loadLogs)
</script>
