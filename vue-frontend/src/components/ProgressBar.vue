<template>
  <div class="w-full">
    <div class="flex items-center justify-between mb-2">
      <span class="text-sm font-medium text-gray-700">{{ status }}</span>
      <span class="text-sm text-gray-500">{{ progress }}%</span>
    </div>

    <div class="w-full bg-gray-200 rounded-full h-3">
      <div
        class="h-3 rounded-full transition-all duration-500 ease-out"
        :class="[
          progress < 30 ? 'bg-blue-500' :
          progress < 60 ? 'bg-yellow-500' :
          progress < 90 ? 'bg-orange-500' :
          'bg-green-500'
        ]"
        :style="{ width: progress + '%' }"
      ></div>
    </div>

    <div class="mt-2 text-xs text-gray-500">
      {{ description }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  progress: number
  status: string
  description?: string
}

withDefaults(defineProps<Props>(), {
  description: ''
})
</script>

