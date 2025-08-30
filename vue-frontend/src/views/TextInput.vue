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

        <div class="flex justify-between items-center mt-2">
          <span class="text-sm text-gray-500">
            {{ characterCount }}/10,000 characters
          </span>
        </div>
      </div>

      <div class="flex justify-center">
        <button
          @click="submitEvaluation"
          :disabled="!canSubmit"
          class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🚀 Submit for Evaluation
        </button>
      </div>

      <div v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const textContent = ref('')
const error = ref('')

const characterCount = computed(() => textContent.value.length)
const canSubmit = computed(() =>
  textContent.value.trim().length > 0 &&
  characterCount.value <= 10000
)

const submitEvaluation = async () => {
  if (!canSubmit.value) return

  // TODO: Implement evaluation submission in Phase 4
  // For now, redirect to overall feedback
  router.push('/overall-feedback')
}
</script>
