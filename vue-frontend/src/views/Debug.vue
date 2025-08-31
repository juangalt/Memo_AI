<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Debug Panel
        </h1>
        
        <div class="grid md:grid-cols-2 gap-6">
          <!-- System Diagnostics -->
          <div class="bg-red-50 rounded-lg p-6 border-l-4 border-red-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🔍 System Diagnostics
            </h3>
            <SystemDiagnostics />
          </div>
          
          <!-- API Health Testing -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-blue-900 mb-4">API Health Testing</h3>
            <ApiHealthTesting />
          </div>

          <!-- Evaluation Testing -->
          <div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 class="text-lg font-semibold text-purple-900 mb-4">Evaluation Endpoint Testing</h3>
            <EvaluationTesting />
          </div>
          
          <!-- Performance Monitoring -->
          <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              📊 Performance Monitoring
            </h3>
            <PerformanceMonitoring />
          </div>
          
          <!-- Development Tools -->
          <div class="bg-purple-50 rounded-lg p-6 border-l-4 border-purple-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🛠️ Development Tools
            </h3>
            <DevelopmentTools />
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
import SystemDiagnostics from '@/components/debug/SystemDiagnostics.vue'
import ApiHealthTesting from '@/components/debug/ApiHealthTesting.vue'
import PerformanceMonitoring from '@/components/debug/PerformanceMonitoring.vue'
import DevelopmentTools from '@/components/debug/DevelopmentTools.vue'
import EvaluationTesting from '@/components/debug/EvaluationTesting.vue'
</script>
