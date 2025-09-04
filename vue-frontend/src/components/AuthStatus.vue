<template>
  <div class="flex items-center space-x-3">
    <!-- Status Indicator -->
    <div class="flex items-center">
      <div
        class="w-2 h-2 rounded-full"
        :class="isAuthenticated ? 'bg-green-500' : 'bg-gray-400'"
      ></div>
      <span class="ml-2 text-sm text-gray-600">
        {{ isAuthenticated ? 'Authenticated' : 'Not Authenticated' }}
      </span>
    </div>

    <!-- User Info -->
    <div v-if="isAuthenticated" class="flex items-center space-x-2">
      <span class="text-sm text-gray-700">{{ username }}</span>
      <span
        v-if="isAdmin"
        class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
      >
        Admin
      </span>
    </div>

    <!-- Logout Button -->
    <button
      v-if="isAuthenticated"
      @click="handleLogout"
      class="text-sm font-bold text-gray-500 hover:text-gray-700 transition-colors"
    >
      Logout
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

