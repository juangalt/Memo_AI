import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { evaluationService } from '@/services/evaluation'

interface Evaluation {
  id: string
  overall_score: number
  strengths: string[]
  opportunities: string[]
  rubric_scores: Record<string, any>
  processing_time: number
  created_at: string
}

interface EvaluationState {
  currentEvaluation: Evaluation | null
  evaluationHistory: Evaluation[]
  isLoading: boolean
  error: string | null
}

export const useEvaluationStore = defineStore('evaluation', () => {
  // State
  const currentEvaluation = ref<Evaluation | null>(null)
  const evaluationHistory = ref<Evaluation[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasEvaluation = computed(() => !!currentEvaluation.value)
  const hasHistory = computed(() => evaluationHistory.value.length > 0)

  // Actions
  const submitEvaluation = async (textContent: string): Promise<Evaluation | null> => {
    isLoading.value = true
    error.value = null

    try {
      const result = await evaluationService.submitEvaluation(textContent)

      if (result.success) {
        // Debug: Log the result structure
        console.log('Evaluation result:', result)
        console.log('Result data:', result.data)
        
        // Check if result.data exists and has evaluation property
        if (!result.data) {
          error.value = 'No data received from evaluation service'
          return null
        }
        
        if (!result.data.evaluation) {
          error.value = 'No evaluation data in response'
          console.error('Missing evaluation in result.data:', result.data)
          return null
        }
        
        // Store the evaluation result
        const evaluation = result.data.evaluation
        currentEvaluation.value = evaluation

        // Add to history (keeping last 10 evaluations)
        evaluationHistory.value.unshift(evaluation)
        if (evaluationHistory.value.length > 10) {
          evaluationHistory.value = evaluationHistory.value.slice(0, 10)
        }

        return evaluation
      } else {
        // Handle evaluation errors
        error.value = result.error || 'Evaluation failed'
        return null
      }
    } catch (err: any) {
      error.value = err.message || 'Evaluation failed'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const getEvaluation = async (evaluationId: string): Promise<Evaluation | null> => {
    isLoading.value = true
    error.value = null

    try {
      const result = await evaluationService.getEvaluation(evaluationId)

      if (result.success) {
        const evaluation = result.data.evaluation
        currentEvaluation.value = evaluation
        return evaluation
      } else {
        error.value = result.error || 'Failed to retrieve evaluation'
        return null
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to retrieve evaluation'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const clearEvaluation = () => {
    currentEvaluation.value = null
    error.value = null
  }

  const clearHistory = () => {
    evaluationHistory.value = []
  }

  return {
    // State
    currentEvaluation,
    evaluationHistory,
    isLoading,
    error,

    // Getters
    hasEvaluation,
    hasHistory,

    // Actions
    submitEvaluation,
    getEvaluation,
    clearEvaluation,
    clearHistory
  }
})
