<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Mobile Menu Overlay -->
    <div 
      v-if="isMobileMenuOpen" 
      class="fixed inset-0 z-40 lg:hidden"
      @click="closeMobileMenu"
    >
      <div class="fixed inset-0 bg-gray-600 bg-opacity-75"></div>
    </div>

    <!-- Left Sidebar Navigation -->
    <aside 
      class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-sm border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0"
      :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo and Title in Sidebar -->
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-xl font-semibold text-gray-900">📝 Memo AI Coach</h1>
      </div>

      <!-- Navigation Menu -->
      <nav class="p-4 space-y-2">
        <router-link
          to="/text-input"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/text-input' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">📝</span>
          <span class="font-medium">Text Input</span>
        </router-link>
        
        <router-link
          to="/overall-feedback"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/overall-feedback' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">📊</span>
          <span class="font-medium">Overall Feedback</span>
        </router-link>
        
        <router-link
          to="/detailed-feedback"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/detailed-feedback' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">🔍</span>
          <span class="font-medium">Detailed Feedback</span>
        </router-link>
        
        <router-link
          to="/help"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/help' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">📚</span>
          <span class="font-medium">Help</span>
        </router-link>
        
        <!-- Admin Section Divider -->
        <div v-if="isAdmin" class="pt-4 mt-4 border-t border-gray-200">
          <div class="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Admin Tools
          </div>
        </div>
        
        <router-link
          v-if="isAdmin"
          to="/admin"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/admin' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">⚙️</span>
          <span class="font-medium">Admin</span>
        </router-link>
        
        <router-link
          v-if="isAdmin"
          to="/last-evaluation"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/last-evaluation' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">🔍</span>
          <span class="font-medium">Last Evaluation</span>
        </router-link>
        
        <router-link
          v-if="isAdmin"
          to="/debug"
          class="flex items-center px-4 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors"
          :class="{ 'text-blue-600 bg-blue-50 border-r-2 border-blue-600': $route.path === '/debug' }"
          @click="closeMobileMenu"
        >
          <span class="text-lg mr-3">🐛</span>
          <span class="font-medium">Debug</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col lg:ml-0">
      <!-- Top Header with Auth Status -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="px-4 sm:px-6 lg:px-8 py-4">
          <div class="flex justify-between items-center">
            <!-- Mobile Menu Button -->
            <button
              @click="toggleMobileMenu"
              class="lg:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <!-- Spacer for mobile -->
            <div class="lg:hidden flex-1"></div>

            <!-- Auth Status -->
            <AuthStatus />
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="flex-1 p-4 sm:p-6">
        <slot />
      </main>

      <!-- Footer -->
      <footer class="bg-white border-t border-gray-200 py-4">
        <div class="text-center">
          <p class="text-sm text-gray-500">
            © FGS
          </p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import AuthStatus from './AuthStatus.vue'

// Use the global auth store instance that the router also uses
const authStore = computed(() => (window as any).authStoreInstance)
const isAdmin = computed(() => authStore.value?.isAdmin || false)

// Mobile menu state
const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}
</script>

