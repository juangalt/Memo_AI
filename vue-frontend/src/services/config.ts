import { apiClient } from './api'

interface FrontendConfig {
  session_warning_threshold: number
  session_refresh_interval: number
  debug_console_log_limit: number
  llm_timeout_expectation: number
  default_response_time: number
}

export const configService = {
  async getFrontendConfig(): Promise<FrontendConfig> {
    try {
      const response = await apiClient.get<FrontendConfig>('/api/v1/config/frontend')
      if (response.success && response.data) {
        return response.data
      }
      throw new Error('Failed to load frontend configuration')
    } catch (error) {
      console.error('Error loading frontend configuration:', error)
      // Return default values if configuration loading fails
      return {
        session_warning_threshold: 10,
        session_refresh_interval: 60,
        debug_console_log_limit: 50,
        llm_timeout_expectation: 15,
        default_response_time: 1000
      }
    }
  }
}
