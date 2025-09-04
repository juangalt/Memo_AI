<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo and Title -->
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">📝 Memo AI Coach</h1>
          </div>

          <!-- Navigation Tabs -->
          <nav class="flex space-x-8">
            <router-link
              to="/text-input"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/text-input' }"
            >
              📝 Text Input
            </router-link>
            <router-link
              to="/overall-feedback"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/overall-feedback' }"
            >
              📊 Overall Feedback
            </router-link>
            <router-link
              to="/detailed-feedback"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/detailed-feedback' }"
            >
              🔍 Detailed Feedback
            </router-link>
            <router-link
              to="/help"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/help' }"
            >
              📚 Help
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/admin"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/admin' }"
            >
              ⚙️ Admin
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/last-evaluation"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/last-evaluation' }"
            >
              🔍 Last Evaluation
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/debug"
              class="text-gray-500 hover:text-gray-700 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="{ 'text-blue-600 bg-blue-50': $route.path === '/debug' }"
            >
              🐛 Debug
            </router-link>
          </nav>

          <!-- Auth Status -->
          <AuthStatus />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="text-center">
          <p class="text-sm text-gray-500">
            © Copyright FGS
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AuthStatus from './AuthStatus.vue'

// Use the global auth store instance that the router also uses
const authStore = computed(() => (window as any).authStoreInstance)
const isAdmin = computed(() => authStore.value?.isAdmin || false)
</script>

