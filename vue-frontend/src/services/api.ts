import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'

export interface APIResponse<T = any> {
  success: boolean
  data: T | null
  error?: string
  status?: number
}

class APIClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Memo-AI-Coach-Vue/1.0.0'
      }
    })

    // Request interceptor for authentication headers
    this.client.interceptors.request.use(
      (config) => {
        // Get token from auth store (memory only, per auth specs)
        const authStore = (window as any).authStoreInstance
        const token = authStore?.sessionToken || null
        if (token) {
          config.headers['X-Session-Token'] = token
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear session on auth errors per auth specs
          const authStore = (window as any).authStoreInstance
          if (authStore) {
            authStore.logout()
          }
          // Redirect to login page
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  private async request<T>(
    method: string,
    endpoint: string,
    data: any = null,
    config: AxiosRequestConfig = {}
  ): Promise<APIResponse<T>> {
    try {
      const response: AxiosResponse = await this.client.request({
        method,
        url: endpoint,
        data,
        ...config
      })

      // Handle standardized response format
      if (response.data && typeof response.data === 'object') {
        const { data, meta, errors } = response.data

        if (errors && Array.isArray(errors) && errors.length > 0) {
          return {
            success: false,
            data: null,
            error: errors[0].message,
            status: errors[0].code
          }
        }

        return {
          success: true,
          data: data,
          status: response.status
        }
      }

      return {
        success: true,
        data: response.data,
        status: response.status
      }
    } catch (error: any) {
      return {
        success: false,
        data: null,
        error: error.response?.data?.detail || error.message,
        status: error.response?.status
      }
    }
  }

  get<T>(endpoint: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>('GET', endpoint, null, config)
  }

  post<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>('POST', endpoint, data, config)
  }

  put<T>(endpoint: string, data?: any, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>('PUT', endpoint, data, config)
  }

  delete<T>(endpoint: string, config?: AxiosRequestConfig): Promise<APIResponse<T>> {
    return this.request<T>('DELETE', endpoint, null, config)
  }
}

export const apiClient = new APIClient()
