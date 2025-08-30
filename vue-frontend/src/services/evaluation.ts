import { apiClient } from './api'

interface EvaluationRequest {
  text_content: string
}

interface EvaluationResponse {
  evaluation: {
    id: string
    overall_score: number
    strengths: string[]
    opportunities: string[]
    rubric_scores: Record<string, any>
    processing_time: number
    created_at: string
  }
  meta: {
    timestamp: string
    request_id: string
  }
}

export const evaluationService = {
  async submitEvaluation(textContent: string) {
    const result = await apiClient.post<EvaluationResponse>('/api/v1/evaluations/submit', {
      text_content: textContent
    })

    if (result.success) {
      // Handle standardized response format
      const { data, meta, errors } = result.data

      if (errors && Array.isArray(errors) && errors.length > 0) {
        return {
          success: false,
          error: errors[0].message,
          status: errors[0].code
        }
      }

      return {
        success: true,
        data: data,
        meta: meta
      }
    }

    return result
  },

  async getEvaluation(evaluationId: string) {
    const result = await apiClient.get<EvaluationResponse>(`/api/v1/evaluations/${evaluationId}`)

    if (result.success) {
      const { data, meta, errors } = result.data
      return {
        success: true,
        data: data,
        meta: meta,
        errors: errors
      }
    }

    return result
  }
}
