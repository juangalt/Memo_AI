<template>
  <div class="flex items-center space-x-4">
    <!-- Status Indicator -->
    <div class="flex items-center">
      <div
        class="w-3 h-3 rounded-full"
        :class="isAuthenticated ? 'bg-green-500' : 'bg-gray-400'"
      ></div>
      <span class="ml-2 text-sm font-medium text-gray-700">
        {{ isAuthenticated ? $t('auth.authenticated') : $t('auth.notAuthenticated') }}
      </span>
    </div>

    <!-- User Info -->
    <div v-if="isAuthenticated" class="flex items-center space-x-3">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <span class="text-sm font-semibold text-blue-600">{{ username.charAt(0).toUpperCase() }}</span>
        </div>
        <div class="flex flex-col">
          <span class="text-sm font-semibold text-gray-900">{{ username }}</span>
          <span
            v-if="isAdmin"
            class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
          >
            {{ $t('auth.admin') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Logout Button -->
    <button
      v-if="isAuthenticated"
      @click="handleLogout"
      class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
    >
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
      </svg>
      {{ $t('auth.logout') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()

// Use the global auth store instance that the router also uses
const authStore = computed(() => (window as any).authStoreInstance)

const isAuthenticated = computed(() => authStore.value?.isAuthenticated || false)
const isAdmin = computed(() => authStore.value?.isAdmin || false)
const username = computed(() => authStore.value?.username || '')

const handleLogout = async () => {
  if (authStore.value) {
    await authStore.value.logout()
    router.push('/')
  }
}
</script>

