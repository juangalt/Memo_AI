<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <div class="mb-6">
          <h1 class="text-3xl font-bold text-gray-900">
            🔍 Last Evaluations Raw Data
          </h1>
          <p class="text-gray-600 mt-2">
            View raw LLM prompts and responses for debugging and monitoring purposes.
          </p>
        </div>
        
        <LastEvaluationsViewer />
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
import LastEvaluationsViewer from '@/components/admin/LastEvaluationsViewer.vue'
</script>
