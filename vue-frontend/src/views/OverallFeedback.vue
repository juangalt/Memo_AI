<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          {{ $t('feedback.overallTitle') }}
        </h1>

        <div v-if="hasEvaluation" class="space-y-8">
          <div class="text-center">
            <div class="bg-blue-50 rounded-lg p-8 border-l-4 border-blue-500">
              <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                {{ $t('feedback.overallScore') }}
              </h2>
              <div class="text-6xl font-bold text-blue-600">
                {{ overallScore }}/5.0
              </div>
              <div class="mt-2 text-sm text-gray-600">
                {{ getScoreDescription(overallScore) }}
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6">
            <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                💪 {{ $t('feedback.strengths') }}
              </h3>
              <ul v-if="strengths.length" class="space-y-2">
                <li v-for="strength in strengths" :key="strength" class="flex items-start">
                  <span class="text-green-500 mr-2 mt-1">•</span>
                  <span>{{ strength }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600 italic">{{ $t('feedback.noStrengths') }}</p>
            </div>

            <div class="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                🎯 {{ $t('feedback.opportunities') }}
              </h3>
              <ul v-if="opportunities.length" class="space-y-2">
                <li v-for="opportunity in opportunities" :key="opportunity" class="flex items-start">
                  <span class="text-yellow-500 mr-2 mt-1">•</span>
                  <span>{{ opportunity }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600 italic">{{ $t('feedback.noOpportunities') }}</p>
            </div>
          </div>

          <DynamicRubricScores :scores="rubricScores" :overall-score="overallScore" />

          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex justify-between items-center text-sm text-gray-600">
              <div class="flex items-center space-x-4">
                <span>📊 {{ $t('feedback.processingTime') }}: {{ processingTime }}s</span>
                <span>📅 {{ $t('feedback.created') }}: {{ formatDate(createdAt) }}</span>
              </div>
              <div class="flex space-x-2">
                <router-link
                  to="/detailed-feedback"
                  class="px-4 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition-colors"
                >
                  {{ $t('feedback.viewDetailed') }}
                </router-link>
                <router-link
                  to="/text-input"
                  class="px-4 py-2 bg-gray-600 text-white rounded text-sm hover:bg-gray-700 transition-colors"
                >
                  {{ $t('feedback.submitNew') }}
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-12">
          <div class="text-gray-600">
            <div class="text-6xl mb-4">📝</div>
            <p class="text-lg mb-4">{{ $t('feedback.noEvaluation') }}</p>
            <p class="text-sm mb-6">{{ $t('feedback.noEvaluationDesc') }}</p>
            <router-link
              to="/text-input"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              🚀 {{ $t('feedback.submitText') }}
            </router-link>
          </div>
        </div>

        <div v-if="isLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="text-sm text-gray-600 mt-2">{{ $t('feedback.loading') }}</p>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useEvaluationStore } from '@/stores/evaluation'
import Layout from '@/components/Layout.vue'
import DynamicRubricScores from '@/components/DynamicRubricScores.vue'

const { t } = useI18n()
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
  if (score >= 4.5) return t('scoring.outstanding')
  if (score >= 4.0) return t('scoring.veryGood')
  if (score >= 3.5) return t('scoring.good')
  if (score >= 3.0) return t('scoring.fair')
  if (score >= 2.0) return t('scoring.needsImprovement')
  return t('scoring.requiresRevision')
}
</script>
