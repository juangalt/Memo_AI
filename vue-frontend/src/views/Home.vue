<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex flex-col">
    <!-- Header -->
    <header class="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-2">
            📝 Memo AI Coach
          </h1>
          <p class="text-lg text-gray-600">
            Intelligent text evaluation and feedback system
          </p>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="flex-1 max-w-6xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <div class="mb-8">
          <div class="text-8xl mb-6">🚀</div>
          <h2 class="text-5xl font-bold text-gray-900 mb-6">
            Welcome to Memo AI Coach
          </h2>
          <p class="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Transform your writing with AI-powered evaluation and personalized feedback. 
            Get comprehensive insights to improve your business memos and professional communication.
          </p>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
          <router-link
            :to="isAuthenticated ? '/text-input' : '/login'"
            class="inline-flex items-center px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            🔑 Log In
          </router-link>
          <button
            @click="scrollToFeatures"
            class="inline-flex items-center px-8 py-4 bg-white text-gray-700 text-lg font-semibold rounded-lg border-2 border-gray-300 hover:border-blue-500 hover:text-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-1"
          >
            ✨ Learn More
          </button>
        </div>
      </div>

      <!-- Features Section -->
      <div ref="featuresSection" class="grid md:grid-cols-3 gap-8 mb-16">
        <div class="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-2">
          <div class="text-4xl mb-4">🎯</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-3">Smart Evaluation</h3>
          <p class="text-gray-600">
            Advanced AI analyzes your text against comprehensive rubrics, providing detailed scoring and insights.
          </p>
        </div>

        <div class="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-2">
          <div class="text-4xl mb-4">💡</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-3">Actionable Feedback</h3>
          <p class="text-gray-600">
            Receive specific, actionable suggestions to improve clarity, structure, and impact of your writing.
          </p>
        </div>

        <div class="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-2">
          <div class="text-4xl mb-4">📊</div>
          <h3 class="text-xl font-semibold text-gray-900 mb-3">Detailed Analytics</h3>
          <p class="text-gray-600">
            Comprehensive breakdown of strengths and opportunities with segment-level feedback for targeted improvement.
          </p>
        </div>
      </div>

      <!-- How It Works Section -->
      <div class="bg-white rounded-2xl p-8 shadow-lg mb-16">
        <h3 class="text-3xl font-bold text-gray-900 text-center mb-8">How It Works</h3>
        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">1</span>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Submit Your Text</h4>
            <p class="text-gray-600">Paste your memo or business text into our evaluation system.</p>
          </div>
          <div class="text-center">
            <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">2</span>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">AI Analysis</h4>
            <p class="text-gray-600">Our AI evaluates your text using comprehensive business writing criteria.</p>
          </div>
          <div class="text-center">
            <div class="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span class="text-2xl">3</span>
            </div>
            <h4 class="text-lg font-semibold text-gray-900 mb-2">Get Feedback</h4>
            <p class="text-gray-600">Receive detailed feedback with scores, strengths, and improvement suggestions.</p>
          </div>
        </div>
      </div>

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
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const featuresSection = ref<HTMLElement>()

const scrollToFeatures = () => {
  featuresSection.value?.scrollIntoView({ 
    behavior: 'smooth',
    block: 'start'
  })
}
</script>
