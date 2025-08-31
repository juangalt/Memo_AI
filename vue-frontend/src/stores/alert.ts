import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Alert {
  id: string
  message: string
  type: 'success' | 'warning' | 'error' | 'info'
  details?: string
  show: boolean
  duration?: number
}

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<Alert[]>([])

  const showAlert = (message: string, type: 'success' | 'warning' | 'error' | 'info' = 'info', duration = 5000) => {
    const id = Date.now().toString()
    const alert: Alert = {
      id,
      message,
      type,
      show: true,
      duration
    }
    
    alerts.value.push(alert)

    if (duration > 0) {
      setTimeout(() => {
        hideAlert(id)
      }, duration)
    }

    return id
  }

  const hideAlert = (id: string) => {
    const alert = alerts.value.find(a => a.id === id)
    if (alert) {
      alert.show = false
      setTimeout(() => {
        alerts.value = alerts.value.filter(a => a.id !== id)
      }, 300)
    }
  }

  const showSuccess = (message: string, details?: string) => {
    return showAlert(message, 'success', details ? 7000 : 5000)
  }

  const showError = (message: string, details?: string) => {
    return showAlert(message, 'error', details ? 10000 : 7000)
  }

  const showWarning = (message: string, details?: string) => {
    return showAlert(message, 'warning', details ? 8000 : 6000)
  }

  const showInfo = (message: string, details?: string) => {
    return showAlert(message, 'info', details ? 6000 : 4000)
  }

  const clearAll = () => {
    alerts.value.forEach(alert => {
      alert.show = false
    })
    setTimeout(() => {
      alerts.value = []
    }, 300)
  }

  return {
    alerts,
    showAlert,
    hideAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    clearAll
  }
})

