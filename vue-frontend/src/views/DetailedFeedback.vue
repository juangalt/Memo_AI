<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Detailed Feedback
        </h1>

        <div class="text-center py-12">
          <div class="text-gray-500">
            <p class="text-lg mb-4">📊 Detailed feedback will be displayed here</p>
            <router-link
              to="/text-input"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Text Input
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
// Detailed feedback component - will be implemented in Phase 7
</script>
