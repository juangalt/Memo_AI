<template>
  <div class="space-y-4">
    <div v-if="isLoading" class="text-center">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-green-600 mx-auto"></div>
      <p class="text-sm text-gray-600 mt-2">Validating configuration...</p>
    </div>
    
    <div v-else class="space-y-3">
      <!-- Configuration Files -->
      <div v-for="config in configFiles" :key="config.name" class="bg-white rounded-lg border p-3">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center">
            <span class="text-lg mr-2">📄</span>
            <span class="font-medium">{{ config.name }}</span>
          </div>
          <span :class="getValidationClass(config.status)" class="px-2 py-1 rounded-full text-xs font-medium">
            {{ config.status }}
          </span>
        </div>
        
        <div v-if="config.errors && config.errors.length > 0" class="mt-2">
          <div class="text-xs text-red-600 font-medium mb-1">Validation Errors:</div>
          <ul class="text-xs text-red-600 space-y-1">
            <li v-for="error in config.errors" :key="error" class="flex items-start">
              <span class="text-red-500 mr-1">•</span>
              <span>{{ error }}</span>
            </li>
          </ul>
        </div>
        
        <div v-if="config.warnings && config.warnings.length > 0" class="mt-2">
          <div class="text-xs text-yellow-600 font-medium mb-1">Warnings:</div>
          <ul class="text-xs text-yellow-600 space-y-1">
            <li v-for="warning in config.warnings" :key="warning" class="flex items-start">
              <span class="text-yellow-500 mr-1">•</span>
              <span>{{ warning }}</span>
            </li>
          </ul>
        </div>
        
        <div v-if="config.details" class="mt-2 text-xs text-gray-600">
          {{ config.details }}
        </div>
      </div>
    </div>
    
    <!-- Validation Summary -->
    <div class="bg-white rounded-lg border p-3">
      <div class="flex items-center justify-between">
        <span class="font-medium">Validation Summary</span>
        <span :class="summaryClass" class="px-2 py-1 rounded-full text-xs font-medium">
          {{ validationSummary }}
        </span>
      </div>
      <div class="text-xs text-gray-600 mt-1">
        {{ validCount }} valid, {{ errorCount }} errors, {{ warningCount }} warnings
      </div>
    </div>
    
    <!-- Validate Button -->
    <button
      @click="validateConfigs"
      :disabled="isLoading"
      class="w-full mt-4 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      🔍 Validate All Configurations
    </button>
    
    <!-- Last Validated -->
    <div class="text-xs text-gray-500 text-center">
      Last validated: {{ lastValidated }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/services/api'

interface ConfigFile {
  name: string
  status: 'valid' | 'invalid' | 'warning' | 'unknown'
  errors?: string[]
  warnings?: string[]
  details?: string
}

const isLoading = ref(false)
const configFiles = ref<ConfigFile[]>([
  { name: 'rubric.yaml', status: 'unknown' },
  { name: 'prompt.yaml', status: 'unknown' },
  { name: 'llm.yaml', status: 'unknown' },
  { name: 'auth.yaml', status: 'unknown' }
])
const lastValidated = ref('Never')

const validCount = computed(() => configFiles.value.filter(c => c.status === 'valid').length)
const errorCount = computed(() => configFiles.value.filter(c => c.status === 'invalid').length)
const warningCount = computed(() => configFiles.value.filter(c => c.status === 'warning').length)

const validationSummary = computed(() => {
  if (errorCount.value > 0) return 'Errors Found'
  if (warningCount.value > 0) return 'Warnings Found'
  if (validCount.value === configFiles.value.length) return 'All Valid'
  return 'Unknown'
})

const summaryClass = computed(() => {
  switch (validationSummary.value) {
    case 'All Valid': return 'bg-green-100 text-green-800'
    case 'Errors Found': return 'bg-red-100 text-red-800'
    case 'Warnings Found': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
})

const getValidationClass = (status: string) => {
  switch (status) {
    case 'valid': return 'bg-green-100 text-green-800'
    case 'invalid': return 'bg-red-100 text-red-800'
    case 'warning': return 'bg-yellow-100 text-yellow-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const validateConfigs = async () => {
  isLoading.value = true
  try {
    // Validate each configuration file by reading it
    for (const config of configFiles.value) {
      try {
        const configName = config.name.replace('.yaml', '')
        const result = await apiClient.get(`/api/v1/admin/config/${configName}`)
        
        if (result.success) {
          // Configuration loaded successfully
          config.status = 'valid'
          config.errors = []
          config.warnings = []
          const content = (result.data as any)?.content
          config.details = `Configuration loaded successfully (${content?.length || 0} characters)`
        } else {
          config.status = 'invalid'
          config.errors = [result.error || 'Failed to load configuration']
          config.warnings = []
          config.details = 'Configuration could not be loaded'
        }
      } catch (error) {
        config.status = 'invalid'
        config.errors = ['Failed to validate configuration']
        config.warnings = []
        config.details = 'Network error or server unavailable'
        console.error(`Failed to validate ${config.name}:`, error)
      }
    }
    
    lastValidated.value = new Date().toLocaleTimeString()
  } catch (error) {
    console.error('Failed to validate configurations:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  validateConfigs()
})
</script>
