<template>
  <div id="app">
    <!-- Layout wrapper for authenticated routes -->
    <Layout v-if="isAuthenticated">
      <RouterView />
    </Layout>

    <!-- Direct router view for public routes (login, etc.) -->
    <RouterView v-else />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import Layout from '@/components/Layout.vue'

const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>

