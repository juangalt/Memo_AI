<template>
  <div v-if="show" class="fixed top-4 right-4 z-50 max-w-sm">
    <div :class="alertClass" class="rounded-lg p-4 shadow-lg border-l-4">
      <div class="flex items-center">
        <div class="flex-1">
          <p class="text-sm font-medium">{{ message }}</p>
          <p v-if="details" class="text-sm opacity-90 mt-1">{{ details }}</p>
        </div>
        <button @click="$emit('close')" class="ml-3">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show: boolean
  message: string
  details?: string
  type?: 'success' | 'warning' | 'error' | 'info'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info'
})

defineEmits<{
  close: []
}>()

const alertClass = computed(() => {
  const base = 'bg-white'
  switch (props.type) {
    case 'success': return `${base} border-green-500 text-green-700`
    case 'warning': return `${base} border-yellow-500 text-yellow-700`
    case 'error': return `${base} border-red-500 text-red-700`
    default: return `${base} border-blue-500 text-blue-700`
  }
})
</script>

