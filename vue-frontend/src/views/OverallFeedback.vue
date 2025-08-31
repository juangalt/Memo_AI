<template>
  <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Overall Feedback
        </h1>

        <div v-if="hasEvaluation" class="space-y-8">
          <div class="text-center">
            <div class="bg-blue-50 rounded-lg p-8 border-l-4 border-blue-500">
              <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                Overall Score
              </h2>
              <div class="text-6xl font-bold text-blue-600">
                {{ overallScore }}/5.0
              </div>
              <div class="mt-2 text-sm text-gray-600">
                {{ getScoreDescription(overallScore) }}
              </div>
            </div>
          </div>

          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                💪 Strengths
              </h3>
              <ul v-if="strengths.length" class="space-y-2">
                <li v-for="strength in strengths" :key="strength" class="flex items-start">
                  <span class="text-green-500 mr-2 mt-1">•</span>
                  <span>{{ strength }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600 italic">No specific strengths identified</p>
            </div>

            <div class="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                🎯 Opportunities for Improvement
              </h3>
              <ul v-if="opportunities.length" class="space-y-2">
                <li v-for="opportunity in opportunities" :key="opportunity" class="flex items-start">
                  <span class="text-yellow-500 mr-2 mt-1">•</span>
                  <span>{{ opportunity }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600 italic">No improvement opportunities identified</p>
            </div>
          </div>

          <RubricScores :scores="rubricScores" />

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex justify-between items-center text-sm text-gray-600">
              <div class="flex items-center space-x-4">
                <span>📊 Processing Time: {{ processingTime }}s</span>
                <span>📅 Created: {{ formatDate(createdAt) }}</span>
              </div>
              <div class="flex space-x-2">
                <router-link
                  to="/detailed-feedback"
                  class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
                >
                  View Detailed Feedback
                </router-link>
                <router-link
                  to="/text-input"
                  class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
                >
                  Submit New Text
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <div class="text-gray-500">
            <div class="text-6xl mb-4">📝</div>
            <p class="text-lg mb-4">No evaluation results available</p>
            <p class="text-sm mb-6">Submit your text for evaluation to see comprehensive feedback</p>
            <router-link
              to="/text-input"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              🚀 Submit Text for Evaluation
            </router-link>
          </div>
        </div>

        <div v-if="isLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-sm text-gray-600 mt-2">Loading evaluation results...</p>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'
import RubricScores from '@/components/RubricScores.vue'

const evaluationStore = useEvaluationStore()

const hasEvaluation = computed(() => evaluationStore.hasEvaluation)
const evaluation = computed(() => evaluationStore.currentEvaluation)
const isLoading = computed(() => evaluationStore.isLoading)

const overallScore = computed(() => evaluation.value?.overall_score || 0)
const strengths = computed(() => evaluation.value?.strengths || [])
const opportunities = computed(() => evaluation.value?.opportunities || [])
const rubricScores = computed(() => evaluation.value?.rubric_scores || {})
const processingTime = computed(() => evaluation.value?.processing_time || 0)
const createdAt = computed(() => evaluation.value?.created_at || new Date())

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
</script>
