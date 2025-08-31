<template>
  <div class="w-full">
    <div class="w-full bg-gray-200 rounded-full h-2">
      <div
        :class="progressClass"
        :style="{ width: progress + '%' }"
        class="h-2 rounded-full transition-all duration-300"
      ></div>
    </div>
    <p v-if="status" class="text-sm text-gray-600 mt-2">{{ status }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  progress: number
  status?: string
}

const props = defineProps<Props>()

const progressClass = computed(() => {
  if (props.progress < 30) return 'bg-blue-500'
  if (props.progress < 70) return 'bg-yellow-500'
  return 'bg-green-500'
})
</script>

