<template>
  <div id="app">
    <RouterView />
    
    <!-- Alert System -->
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <Alert
        v-for="alert in alerts"
        :key="alert.id"
        :show="alert.show"
        :message="alert.message"
        :type="alert.type"
        :details="alert.details"
        @close="hideAlert(alert.id)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAlertStore } from '@/stores/alert'
import Alert from '@/components/common/Alert.vue'

const authStore = useAuthStore()
const alertStore = useAlertStore()

const alerts = computed(() => alertStore.alerts)
const hideAlert = (id: string) => alertStore.hideAlert(id)
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>

