<template>
  <Layout>
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          {{ $t('textInput.title') }}
        </h1>

        <p class="text-gray-600 mb-6">
          {{ $t('textInput.description') }}
        </p>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            {{ $t('textInput.label') }}
          </label>
          <textarea
            v-model="textContent"
            :maxlength="10000"
            rows="12"
            @keydown.ctrl.enter.prevent="submitEvaluation"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :placeholder="$t('textInput.placeholder')"
          />

          <div class="mt-2">
            <CharacterCounter :characterCount="characterCount" :max="10000" />
          </div>
        </div>

        <div class="flex justify-center">
          <button
            @click="submitEvaluation"
            :disabled="!canSubmit || isSubmitting"
            class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:bg-gray-400"
          >
            {{ $t('textInput.submitButton') }}
          </button>
        </div>

        <ProgressBar
          v-if="isSubmitting"
          :progress="progress"
          :status="status"
          :description="progressDescription"
        />

        <div v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
import Layout from '@/components/Layout.vue'
import CharacterCounter from '@/components/CharacterCounter.vue'
import ProgressBar from '@/components/ProgressBar.vue'

const router = useRouter()
const evaluationStore = useEvaluationStore()

const textContent = ref('')
const isSubmitting = ref(false)
const progress = ref(0)
const status = ref('')
const progressDescription = ref('')

const characterCount = computed(() => textContent.value.length)
const canSubmit = computed(() =>
  textContent.value.trim().length > 0 &&
  characterCount.value <= 10000 &&
  !isSubmitting.value
)

const error = computed(() => evaluationStore.error)

const submitEvaluation = async () => {
  if (!canSubmit.value) return

  isSubmitting.value = true
  progress.value = 0
  status.value = '📝 ' + $t('textInput.analyzingStructure')
  progressDescription.value = $t('textInput.preparingText')

  try {
    const progressInterval = setInterval(() => {
      progress.value = Math.min(progress.value + 1, 100)
      if (progress.value <= 30) {
        status.value = '📝 ' + $t('textInput.analyzingStructure')
        progressDescription.value = $t('textInput.breakingDownContent')
      } else if (progress.value <= 60) {
        status.value = '🧠 ' + $t('textInput.processingWithAI')
        progressDescription.value = $t('textInput.aiEvaluating')
      } else if (progress.value <= 90) {
        status.value = '📊 ' + $t('textInput.generatingFeedback')
        progressDescription.value = $t('textInput.creatingRecommendations')
      } else {
        status.value = '✅ ' + $t('textInput.finalizingEvaluation')
        progressDescription.value = $t('textInput.almostDone')
      }
    }, 50)

    const result = await evaluationStore.submitEvaluation(textContent.value)

    clearInterval(progressInterval)
    progress.value = 100

    if (result) {
      router.push('/overall-feedback')
    }
  } catch (err: any) {
    console.error('Evaluation failed:', err)
  } finally {
    isSubmitting.value = false
  }
}
</script>
