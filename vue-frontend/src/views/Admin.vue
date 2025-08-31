<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Admin Panel
        </h1>
        
        <div class="grid md:grid-cols-2 gap-6">
          <!-- Health Monitoring -->
          <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🏥 Health Monitoring
            </h3>
            <HealthStatus />
          </div>
          
          <!-- Configuration Validation -->
          <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              ✅ Configuration Validation
            </h3>
            <ConfigValidator />
          </div>
          
          <!-- User Management -->
          <div class="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              👥 User Management
            </h3>
            <UserManagement />
          </div>
          
          <!-- Session Management -->
          <div class="bg-purple-50 rounded-lg p-6 border-l-4 border-purple-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🔗 Session Management
            </h3>
            <SessionManagement />
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
import HealthStatus from '@/components/admin/HealthStatus.vue'
import ConfigValidator from '@/components/admin/ConfigValidator.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import SessionManagement from '@/components/admin/SessionManagement.vue'
</script>
