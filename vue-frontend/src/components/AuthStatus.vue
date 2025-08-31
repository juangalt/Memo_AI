<template>
  <div class="flex items-center space-x-2">
    <div class="flex items-center space-x-1">
      <div
        class="w-2 h-2 rounded-full"
        :class="isAuthenticated ? 'bg-green-500' : 'bg-red-500'"
      ></div>
      <span class="text-sm text-gray-600">
        {{ isAuthenticated ? 'Authenticated' : 'Not Authenticated' }}
      </span>
    </div>

    <div v-if="isAuthenticated" class="text-sm text-gray-600">
      <span class="font-medium">{{ username }}</span>
      <span v-if="isAdmin" class="ml-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
        Admin
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.username)
const isAdmin = computed(() => authStore.isAdmin)
</script>
