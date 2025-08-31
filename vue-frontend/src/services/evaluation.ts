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
      // The API client already processed the response format
      // result.data contains the actual response data
      return {
        success: true,
        data: result.data,
        meta: result.data?.meta || null
      }
    }

    return result
  },

  async getEvaluation(evaluationId: string) {
    const result = await apiClient.get<EvaluationResponse>(`/api/v1/evaluations/${evaluationId}`)

    if (result.success) {
      // The API client already processed the response format
      return {
        success: true,
        data: result.data,
        meta: result.data?.meta || null
      }
    }

    return result
  }
}
