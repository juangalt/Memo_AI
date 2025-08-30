import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useAuthStore } from '@/stores/auth'
import './assets/styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize authentication store globally for API client access
const authStore = useAuthStore()
;(window as any).authStoreInstance = authStore

// Initialize session validation on app startup
// Note: Per auth specs, tokens are stored in memory only
authStore.initializeFromMemory()

// Try to validate existing session on app load
authStore.validateSession().catch(() => {
  // Session validation failed, user will be redirected to login if needed
  console.log('No valid session found, proceeding to login')
})

app.mount('#app')

