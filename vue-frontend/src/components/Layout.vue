<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">📝 Memo AI Coach</h1>
          </div>

          <div class="flex items-center space-x-4">
            <AuthStatus />
            <button @click="handleLogout" class="text-sm text-gray-500 hover:text-gray-700">
              Logout
            </button>
          </div>
        </div>

        <nav class="flex space-x-8">
          <router-link
            v-for="tab in tabs"
            :key="tab.name"
            :to="tab.path"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              $route.path === tab.path
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </router-link>
        </nav>
      </div>
    </header>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthStatus from './AuthStatus.vue'

const router = useRouter()
const authStore = useAuthStore()

const tabs = computed(() => {
  const baseTabs = [
    { name: 'Text Input', path: '/text-input' },
    { name: 'Overall Feedback', path: '/overall-feedback' },
    { name: 'Detailed Feedback', path: '/detailed-feedback' }
  ]

  if (authStore.isAdmin) {
    baseTabs.push(
      { name: 'Admin', path: '/admin' },
      { name: 'Debug', path: '/debug' }
    )
  }

  return baseTabs
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
