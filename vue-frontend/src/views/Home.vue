<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-2">
            📝 Memo AI Coach
          </h1>
          <p class="text-lg text-gray-600">
            Vue Frontend Implementation Progress
          </p>
        </div>
      </div>
    </header>

    <!-- Phase Progress -->
    <main class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">
          🚀 Implementation Phases
        </h2>

        <!-- Phase Progress Cards -->
        <div class="space-y-4" v-if="phases.length > 0">
          <div
            v-for="phase in phases"
            :key="phase.id"
            class="border rounded-lg p-4"
            :class="phase.status === 'completed' ? 'border-green-200 bg-green-50' :
                     phase.status === 'in-progress' ? 'border-blue-200 bg-blue-50' :
                     'border-gray-200 bg-gray-50'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <span class="text-2xl">{{ phase.emoji }}</span>
                <div>
                  <h3 class="font-semibold text-gray-900">{{ phase.title }}</h3>
                  <p class="text-sm text-gray-600">{{ phase.description }}</p>
                </div>
              </div>
              <span
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                         phase.status === 'in-progress' ? 'bg-blue-100 text-blue-800' :
                         'bg-gray-100 text-gray-800'"
              >
                {{ phase.statusText }}
              </span>
            </div>

            <!-- Progress bar for in-progress phases -->
            <div v-if="phase.status === 'in-progress' && phase.progress" class="mt-3">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: phase.progress + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ phase.progress }}% complete</p>
            </div>

            <!-- Completion date -->
            <div v-if="phase.completedDate" class="mt-2 text-xs text-gray-500">
              ✅ Completed on {{ formatDate(phase.completedDate) }}
            </div>
          </div>
        </div>

        <!-- All Complete Message -->
        <div class="mt-8 text-center">
          <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <h3 class="text-lg font-semibold text-green-800 mb-2">
              🎉 Implementation Complete!
            </h3>
            <p class="text-green-700">
              All phases have been successfully implemented. The Vue frontend is now fully operational.
            </p>
          </div>

          <!-- Get Started Button - Always visible -->
          <router-link
            to="/login"
            class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔑 Login to Access Features
          </router-link>
          <p class="text-sm text-gray-600 mt-2">
            Access the memo evaluation system and explore all implemented features
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Phase data structure - Updated to reflect actual completion status
const phases = ref([
  {
    id: 'phase1',
    title: 'Phase 1: Project Setup',
    description: 'Vue project structure, build system, and Docker configuration',
    emoji: '🏗️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2025-08-30',
    progress: null
  },
  {
    id: 'phase2',
    title: 'Phase 2: Infrastructure',
    description: 'Docker Compose integration and production deployment',
    emoji: '🐳',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2025-08-30',
    progress: null
  },
  {
    id: 'phase3',
    title: 'Phase 3: Core Application',
    description: 'Vue Router, authentication store, and app structure',
    emoji: '⚛️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2025-08-30',
    progress: null
  },
  {
    id: 'phase4',
    title: 'Phase 4: API Integration',
    description: 'API client service and backend communication',
    emoji: '🔌',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2025-08-30',
    progress: null
  },
  {
    id: 'phase5',
    title: 'Phase 5: UI Components',
    description: 'Core UI components and responsive design',
    emoji: '🎨',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2025-08-30',
    progress: null
  }
])

const hasIncompletePhases = computed(() =>
  phases.value.some(phase => phase.status !== 'completed')
)

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

// Load phase status from changelog file (mounted to container)
onMounted(async () => {
  try {
    // This would load from the mounted changelog file
    // For now, using static data - will be updated dynamically
    console.log('Phase tracking initialized')
  } catch (error) {
    console.error('Failed to load phase status:', error)
  }
})
</script>
