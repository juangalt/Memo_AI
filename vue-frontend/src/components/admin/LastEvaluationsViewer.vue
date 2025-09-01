<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-900">
        🔍 Last Evaluations Raw Data
      </h3>
      <button
        @click="refreshData"
        :disabled="loading"
        class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Evaluations List -->
    <div class="space-y-4">
      <div
        v-for="evaluation in evaluations"
        :key="evaluation.id"
        class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
      >
        <div class="flex justify-between items-start mb-3">
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-medium text-gray-900">
                {{ evaluation.username }}
              </span>
              <span v-if="evaluation.is_admin" class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                Admin
              </span>
              <span class="text-sm text-gray-500">
                {{ formatDate(evaluation.created_at) }}
              </span>
            </div>
            <div class="text-sm text-gray-600 mt-1">
              Score: {{ evaluation.overall_score }} | 
              Time: {{ evaluation.processing_time }}s | 
              Model: {{ evaluation.llm_model }}
            </div>
          </div>
          <button
            v-if="evaluation.has_raw_data"
            @click="viewRawData(evaluation)"
            class="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            View Raw Data
          </button>
          <span v-else class="text-sm text-gray-400">No Raw Data</span>
        </div>
        <div class="text-sm text-gray-500">
          {{ evaluation.submission_preview }}
        </div>
      </div>
    </div>

    <!-- Raw Data Modal -->
    <div
      v-if="showRawDataModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeRawDataModal"
    >
      <div
        class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h4 class="text-xl font-semibold text-gray-900">
            Raw LLM Data - Evaluation #{{ selectedEvaluation?.id }}
          </h4>
          <button @click="closeRawDataModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div v-if="rawDataLoading" class="text-center py-8">
          <div class="text-gray-500">Loading raw data...</div>
        </div>

        <div v-else-if="rawData" class="space-y-6">
          <!-- Submission Content -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Original Submission</h5>
              <button
                @click="copyToClipboard(rawData.submission.content)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.submission.content"
              :max-height="200"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>

          <!-- Raw Prompt -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Raw Prompt Sent to LLM</h5>
              <button
                @click="copyToClipboard(rawData.evaluation.raw_prompt)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.evaluation.raw_prompt"
              :max-height="300"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>

          <!-- Raw Response -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Raw Response from LLM</h5>
              <button
                @click="copyToClipboard(rawData.evaluation.raw_response)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.evaluation.raw_response"
              :max-height="300"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Success Toast -->
    <div
      v-if="showCopyToast"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50"
    >
      Copied to clipboard!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/services/api'
import CollapsibleText from '@/components/CollapsibleText.vue'

// Types
interface Evaluation {
  id: number
  submission_id: number
  overall_score: number
  processing_time: number
  created_at: string
  llm_provider: string
  llm_model: string
  debug_enabled: boolean
  has_raw_data: boolean
  submission_preview: string
  username: string
  is_admin: boolean
}

interface RawData {
  evaluation: {
    id: number
    submission_id: number
    overall_score: number
    processing_time: number
    created_at: string
    llm_provider: string
    llm_model: string
    debug_enabled: boolean
    raw_prompt: string
    raw_response: string
  }
  submission: {
    id: number
    content: string
    created_at: string
  }
}

// Reactive data
const evaluations = ref<Evaluation[]>([])
const loading = ref(false)
const rawDataLoading = ref(false)
const showRawDataModal = ref(false)
const selectedEvaluation = ref<Evaluation | null>(null)
const rawData = ref<RawData | null>(null)
const showCopyToast = ref(false)

// Methods
const loadEvaluations = async () => {
  try {
    loading.value = true
    const result = await apiClient.get('/api/v1/admin/last-evaluations')
    
    if (result.success) {
      evaluations.value = result.data.evaluations
    }
  } catch (error) {
    console.error('Failed to load evaluations:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadEvaluations()
}

const viewRawData = async (evaluation: Evaluation) => {
  try {
    rawDataLoading.value = true
    showRawDataModal.value = true
    selectedEvaluation.value = evaluation
    
    const result = await apiClient.get(`/api/v1/admin/evaluation/${evaluation.id}/raw`)
    
    if (result.success) {
      rawData.value = result.data.evaluation
    }
  } catch (error) {
    console.error('Failed to load raw data:', error)
  } finally {
    rawDataLoading.value = false
  }
}

const closeRawDataModal = () => {
  showRawDataModal.value = false
  selectedEvaluation.value = null
  rawData.value = null
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    showCopyToast.value = true
    setTimeout(() => {
      showCopyToast.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadEvaluations()
})
</script>
