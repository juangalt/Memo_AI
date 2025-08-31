<template>
  <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Submit Text for Evaluation
        </h1>

        <p class="text-gray-600 mb-6">
          Enter your text below for comprehensive AI-powered evaluation and feedback.
        </p>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Text to Evaluate
          </label>
          <textarea
            v-model="textContent"
            :maxlength="10000"
            rows="12"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your text here (maximum 10,000 characters)..."
          />

          <div class="mt-2">
            <CharacterCounter :characterCount="characterCount" :max="10000" />
          </div>
        </div>

        <div class="flex justify-center">
          <button
            @click="submitEvaluation"
            :disabled="!canSubmit || isSubmitting"
            class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting">🤖 AI is evaluating your text...</span>
            <span v-else>🚀 Submit for Evaluation</span>
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
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
  status.value = '📝 Analyzing text structure...'
  progressDescription.value = 'Preparing your text for AI evaluation'

  try {
    const progressInterval = setInterval(() => {
      progress.value += 1
      if (progress.value <= 30) {
        status.value = '📝 Analyzing text structure...'
        progressDescription.value = 'Breaking down your content for analysis'
      } else if (progress.value <= 60) {
        status.value = '🧠 Processing with AI...'
        progressDescription.value = 'AI is evaluating your writing'
      } else if (progress.value <= 90) {
        status.value = '📊 Generating feedback...'
        progressDescription.value = 'Creating detailed recommendations'
      } else {
        status.value = '✅ Finalizing evaluation...'
        progressDescription.value = 'Almost done!'
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
