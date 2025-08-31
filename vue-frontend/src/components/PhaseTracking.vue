<template>
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

    <!-- Get Started Button -->
    <div class="mt-8 text-center" v-if="hasIncompletePhases">
      <router-link
        to="/login"
        class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        🔑 Login to Access Features
      </router-link>
      <p class="text-sm text-gray-600 mt-2">
        Some features may not be available until implementation is complete
      </p>
    </div>

    <!-- All Complete Message -->
    <div v-else class="mt-8 text-center">
      <div class="bg-green-50 border border-green-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-green-800 mb-2">
          🎉 Implementation Complete!
        </h3>
        <p class="text-green-700">
          All phases have been successfully implemented. The Vue frontend is now fully operational.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Phase data structure
const phases = ref([
  {
    id: 'phase1',
    title: 'Phase 1: Project Setup',
    description: 'Vue project structure, build system, and Docker configuration',
    emoji: '🏗️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-15',
    progress: null
  },
  {
    id: 'phase2',
    title: 'Phase 2: Infrastructure',
    description: 'Docker Compose integration and production deployment',
    emoji: '🐳',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-16',
    progress: null
  },
  {
    id: 'phase3',
    title: 'Phase 3: Core Application',
    description: 'Vue Router, authentication store, and app structure',
    emoji: '⚛️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-17',
    progress: null
  },
  {
    id: 'phase4',
    title: 'Phase 4: API Integration',
    description: 'API client service and backend communication',
    emoji: '🔌',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-18',
    progress: null
  },
  {
    id: 'phase5',
    title: 'Phase 5: UI Components',
    description: 'Core UI components and responsive design',
    emoji: '🎨',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-19',
    progress: null
  },
  {
    id: 'phase6',
    title: 'Phase 6: Core Functionality',
    description: 'Text input, evaluation submission, and progress tracking',
    emoji: '⚙️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-20',
    progress: null
  },
  {
    id: 'phase7',
    title: 'Phase 7: Feedback Display',
    description: 'Overall and detailed feedback components',
    emoji: '📊',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-21',
    progress: null
  },
  {
    id: 'phase8',
    title: 'Phase 8: Admin & Debug',
    description: 'Admin panel, debug tools, and system monitoring',
    emoji: '🛠️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-22',
    progress: null
  },
  {
    id: 'phase9',
    title: 'Phase 9: Production Deployment',
    description: 'Production deployment, optimization, and testing',
    emoji: '🚀',
    status: 'in-progress',
    statusText: 'In Progress',
    completedDate: null,
    progress: 75
  },
  {
    id: 'phase10',
    title: 'Phase 10: Testing & Validation',
    description: 'Comprehensive testing and system validation',
    emoji: '🧪',
    status: 'pending',
    statusText: 'Pending',
    completedDate: null,
    progress: null
  },
  {
    id: 'phase11',
    title: 'Phase 11: Documentation & Handover',
    description: 'Documentation updates and project handover',
    emoji: '📚',
    status: 'pending',
    statusText: 'Pending',
    completedDate: null,
    progress: null
  }
])

const hasIncompletePhases = computed(() =>
  phases.value.some(phase => phase.status !== 'completed')
)

const formatDate = (dateString) => {
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
