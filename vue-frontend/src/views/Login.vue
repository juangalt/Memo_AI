<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          📝 Memo AI Coach
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Intelligent text evaluation and feedback system
        </p>
      </div>

      <div class="bg-white py-8 px-6 shadow rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-6">🔐 Authentication Required</h3>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your username"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <span v-if="isLoading">Loading...</span>
              <span v-else>🔑 Login</span>
            </button>
          </div>
        </form>

        <div v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</div>

        <div v-if="isLoading" class="mt-4 flex items-center justify-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span class="ml-2 text-sm text-gray-600">Authenticating...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const result = await authStore.login(form.value.username, form.value.password)

    if (result.success) {
      // Check if there's a redirect URL in query params
      const redirect = router.currentRoute.value.query.redirect as string
      if (redirect) {
        router.push(redirect)
      } else {
        router.push('/')
      }
    } else {
      // Handle auth spec error codes
      if (result.code === 'AUTH_ACCOUNT_LOCKED') {
        error.value = 'Account temporarily locked due to multiple failed attempts. Please try again later.'
      } else if (result.code === 'AUTH_INVALID_CREDENTIALS') {
        error.value = 'Invalid username or password.'
      } else {
        error.value = result.error || 'Login failed. Please try again.'
      }
    }
  } catch (err: any) {
    error.value = 'Login failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
