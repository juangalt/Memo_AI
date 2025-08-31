<template>
  <div class="space-y-4">
    <!-- Create User Form -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">Create New User</h4>
      <form @submit.prevent="createUser" class="space-y-3">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <input
            v-model="newUser.username"
            type="text"
            placeholder="Username"
            required
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
          <input
            v-model="newUser.password"
            type="password"
            placeholder="Password"
            required
            class="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-500"
          />
        </div>
        <div class="flex items-center">
          <input
            v-model="newUser.isAdmin"
            type="checkbox"
            id="isAdmin"
            class="mr-2"
          />
          <label for="isAdmin" class="text-sm text-gray-700">Admin privileges</label>
        </div>
        <button
          type="submit"
          :disabled="isCreating"
          class="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
        >
          {{ isCreating ? 'Creating...' : 'Create User' }}
        </button>
      </form>
    </div>
    
    <!-- User List -->
    <div class="bg-white rounded-lg border">
      <div class="p-4 border-b">
        <div class="flex items-center justify-between">
          <h4 class="font-medium text-gray-900">User Directory</h4>
          <button
            @click="loadUsers"
            :disabled="isLoading"
            class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            🔄 Refresh
          </button>
        </div>
      </div>
      
      <div v-if="isLoading" class="p-4 text-center">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-600 mx-auto"></div>
        <p class="text-sm text-gray-600 mt-2">Loading users...</p>
      </div>
      
      <div v-else-if="users.length === 0" class="p-4 text-center text-gray-500">
        No users found
      </div>
      
      <div v-else class="divide-y">
        <div
          v-for="user in users"
          :key="user.id"
          class="p-4 flex items-center justify-between"
        >
          <div class="flex items-center space-x-3">
            <div class="flex flex-col">
              <span class="font-medium text-gray-900">{{ user.username }}</span>
              <span class="text-sm text-gray-500">ID: {{ user.id }}</span>
            </div>
            <div class="flex space-x-2">
              <span
                v-if="user.is_admin"
                class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
              >
                Admin
              </span>
              <span
                :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                class="px-2 py-1 text-xs rounded-full"
              >
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </div>
          </div>
          
          <div class="flex items-center space-x-2">
            <span class="text-xs text-gray-500">
              Created: {{ formatDate(user.created_at) }}
            </span>
            <button
              @click="deleteUser(user.username)"
              :disabled="isDeleting === user.username"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {{ isDeleting === user.username ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- User Statistics -->
    <div class="bg-white rounded-lg border p-4">
      <h4 class="font-medium text-gray-900 mb-3">User Statistics</h4>
      <div class="grid grid-cols-2 gap-4 text-center">
        <div>
          <div class="text-2xl font-bold text-blue-600">{{ totalUsers }}</div>
          <div class="text-sm text-gray-600">Total Users</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-purple-600">{{ adminUsers }}</div>
          <div class="text-sm text-gray-600">Administrators</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-green-600">{{ activeUsers }}</div>
          <div class="text-sm text-gray-600">Active Users</div>
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-600">{{ inactiveUsers }}</div>
          <div class="text-sm text-gray-600">Inactive Users</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { apiClient } from '@/services/api'

interface User {
  id: number
  username: string
  is_admin: boolean
  is_active: boolean
  created_at: string
}

const isLoading = ref(false)
const isCreating = ref(false)
const isDeleting = ref<string | null>(null)
const users = ref<User[]>([])

const newUser = ref({
  username: '',
  password: '',
  isAdmin: false
})

const totalUsers = computed(() => users.value.length)
const adminUsers = computed(() => users.value.filter(u => u.is_admin).length)
const activeUsers = computed(() => users.value.filter(u => u.is_active).length)
const inactiveUsers = computed(() => users.value.filter(u => !u.is_active).length)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const loadUsers = async () => {
  isLoading.value = true
  try {
    const result = await apiClient.get('/api/v1/admin/users')
    if (result.success) {
      users.value = result.data.users || result.data || []
    }
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    isLoading.value = false
  }
}

const createUser = async () => {
  isCreating.value = true
  try {
    const result = await apiClient.post('/api/v1/admin/users/create', {
      username: newUser.value.username,
      password: newUser.value.password,
      is_admin: newUser.value.isAdmin
    })
    
    if (result.success) {
      // Reset form
      newUser.value = { username: '', password: '', isAdmin: false }
      // Reload users
      await loadUsers()
    }
  } catch (error) {
    console.error('Failed to create user:', error)
  } finally {
    isCreating.value = false
  }
}

const deleteUser = async (username: string) => {
  if (!confirm(`Are you sure you want to delete user "${username}"?`)) {
    return
  }
  
  isDeleting.value = username
  try {
    const result = await apiClient.delete(`/api/v1/admin/users/${username}`)
    if (result.success) {
      // Reload users
      await loadUsers()
    }
  } catch (error) {
    console.error('Failed to delete user:', error)
  } finally {
    isDeleting.value = null
  }
}

onMounted(() => {
  loadUsers()
})
</script>

