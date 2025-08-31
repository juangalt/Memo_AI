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
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = authStore.isAuthenticated
const isAdmin = authStore.isAdmin
const username = authStore.username

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

