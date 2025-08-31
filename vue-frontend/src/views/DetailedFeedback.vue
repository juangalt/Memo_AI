<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          📊 Detailed Feedback
        </h1>

        <div v-if="hasEvaluation" class="space-y-8">
          <!-- Overall Score Summary -->
          <div class="bg-blue-50 rounded-lg p-4 sm:p-6 border-l-4 border-blue-500">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
              <div>
                <h2 class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                  Overall Evaluation Summary
                </h2>
                <div class="text-2xl sm:text-3xl font-bold text-blue-600">
                  {{ overallScore }}/5.0
                </div>
                <p class="text-xs sm:text-sm text-gray-600 mt-1">
                  {{ getScoreDescription(overallScore) }}
                </p>
              </div>
              <div class="text-left sm:text-right text-xs sm:text-sm text-gray-600">
                <div>Processing Time: {{ processingTime }}s</div>
                <div>Created: {{ formatDate(createdAt) }}</div>
              </div>
            </div>
          </div>

          <!-- Segment Feedback -->
          <div v-if="segmentFeedback.length" class="space-y-4 sm:space-y-6">
            <h3 class="text-xl sm:text-2xl font-semibold text-gray-900">
              📝 Segment-Level Analysis
            </h3>
            
            <div class="space-y-4 sm:space-y-6">
              <div
                v-for="(segment, index) in segmentFeedback"
                :key="index"
                class="border rounded-lg overflow-hidden"
              >
                <!-- Segment Header -->
                <div class="bg-gray-50 px-4 sm:px-6 py-3 sm:py-4 border-b">
                  <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
                    <h4 class="text-base sm:text-lg font-semibold text-gray-900">
                      Segment {{ index + 1 }}
                    </h4>
                    <button
                      @click="toggleSegment(index)"
                      class="text-blue-600 hover:text-blue-800 text-xs sm:text-sm font-medium"
                    >
                      {{ expandedSegments[index] ? 'Collapse' : 'Expand' }}
                    </button>
                  </div>
                </div>

                <!-- Segment Content -->
                <div v-if="expandedSegments[index]" class="p-4 sm:p-6">
                  <!-- Original Text -->
                  <div class="mb-6">
                    <h5 class="text-sm font-medium text-gray-700 mb-2">Original Text:</h5>
                    <div class="bg-gray-50 rounded-lg p-4 text-gray-800 italic">
                      "{{ segment.segment }}"
                    </div>
                  </div>

                  <!-- Comment -->
                  <div class="mb-6">
                    <h5 class="text-sm font-medium text-gray-700 mb-2">💬 Analysis:</h5>
                    <div class="bg-blue-50 rounded-lg p-4 text-gray-800">
                      {{ segment.comment }}
                    </div>
                  </div>

                  <!-- Questions -->
                  <div class="mb-6">
                    <h5 class="text-sm font-medium text-gray-700 mb-2">🤔 Thought-Provoking Questions:</h5>
                    <ul class="space-y-2">
                      <li
                        v-for="(question, qIndex) in segment.questions"
                        :key="qIndex"
                        class="flex items-start"
                      >
                        <span class="text-blue-500 mr-2 mt-1">•</span>
                        <span class="text-gray-800">{{ question }}</span>
                      </li>
                    </ul>
                  </div>

                  <!-- Suggestions -->
                  <div>
                    <h5 class="text-sm font-medium text-gray-700 mb-2">💡 Suggestions for Improvement:</h5>
                    <ul class="space-y-2">
                      <li
                        v-for="(suggestion, sIndex) in segment.suggestions"
                        :key="sIndex"
                        class="flex items-start"
                      >
                        <span class="text-green-500 mr-2 mt-1">•</span>
                        <span class="text-gray-800">{{ suggestion }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- No Segment Feedback -->
          <div v-else class="text-center py-8">
            <div class="text-gray-500">
              <div class="text-4xl mb-4">📝</div>
              <p class="text-lg mb-2">No detailed segment feedback available</p>
              <p class="text-sm">Segment-level analysis will appear here when available</p>
            </div>
          </div>

          <!-- Navigation -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
              <div class="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
                <router-link
                  to="/overall-feedback"
                  class="px-3 sm:px-4 py-2 bg-gray-600 text-white rounded text-xs sm:text-sm hover:bg-gray-700 transition-colors text-center"
                >
                  ← Back to Overall Feedback
                </router-link>
                <router-link
                  to="/text-input"
                  class="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded text-xs sm:text-sm hover:bg-blue-700 transition-colors text-center"
                >
                  Submit New Text
                </router-link>
              </div>
              <div class="text-xs sm:text-sm text-gray-600 text-center sm:text-right">
                {{ segmentFeedback.length }} segments analyzed
              </div>
            </div>
          </div>
        </div>

        <!-- No Evaluation Available -->
        <div v-else class="text-center py-12">
          <div class="text-gray-600">
            <div class="text-6xl mb-4">📊</div>
            <p class="text-lg mb-4">No evaluation results available</p>
            <p class="text-sm mb-6">Submit your text for evaluation to see detailed segment feedback</p>
            <router-link
              to="/text-input"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              🚀 Submit Text for Evaluation
            </router-link>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-sm text-gray-600 mt-2">Loading detailed feedback...</p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'
import Layout from '@/components/Layout.vue'

// Import the SegmentFeedback type from the evaluation store
interface SegmentFeedback {
  segment: string
  comment: string
  questions: string[]
  suggestions: string[]
}

const evaluationStore = useEvaluationStore()

// State
const expandedSegments = ref<Record<number, boolean>>({})

// Computed properties
const hasEvaluation = computed(() => evaluationStore.hasEvaluation)
const evaluation = computed(() => evaluationStore.currentEvaluation)
const isLoading = computed(() => evaluationStore.isLoading)

const overallScore = computed(() => evaluation.value?.overall_score || 0)
const segmentFeedback = computed(() => evaluation.value?.segment_feedback || [])
const processingTime = computed(() => evaluation.value?.processing_time || 0)
const createdAt = computed(() => evaluation.value?.created_at || new Date())

// Methods
const formatDate = (dateString: string | Date): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getScoreDescription = (score: number): string => {
  if (score >= 4.5) return 'Outstanding - Excellent work!'
  if (score >= 4.0) return 'Very Good - Strong performance'
  if (score >= 3.5) return 'Good - Solid work with room for improvement'
  if (score >= 3.0) return 'Fair - Meets basic requirements'
  if (score >= 2.0) return 'Needs Improvement - Significant work required'
  return 'Requires Major Revision - Does not meet basic standards'
}

const toggleSegment = (index: number) => {
  expandedSegments.value[index] = !expandedSegments.value[index]
}

// Initialize all segments as collapsed by default
const initializeSegments = () => {
  segmentFeedback.value.forEach((_: SegmentFeedback, index: number) => {
    expandedSegments.value[index] = false
  })
}

// Watch for changes in segment feedback and initialize
import { watch } from 'vue'
watch(segmentFeedback, () => {
  initializeSegments()
}, { immediate: true })
</script>
