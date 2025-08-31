<template>
  <div class="w-full mt-4">
    <div class="flex items-center justify-between mb-3">
      <span class="text-sm font-medium text-gray-700">{{ status }}</span>
      <span class="text-sm font-bold text-blue-600">{{ progress }}%</span>
    </div>

    <!-- Progress bar container -->
    <div class="w-full bg-gray-300 rounded-lg h-6 border-2 border-gray-400 overflow-hidden">
      <!-- Progress fill -->
      <div
        class="h-full rounded-md transition-all duration-300 ease-out flex items-center justify-center"
        :class="[
          progress < 30 ? 'bg-blue-600' :
          progress < 60 ? 'bg-yellow-500' :
          progress < 90 ? 'bg-orange-500' :
          'bg-green-600'
        ]"
        :style="{ width: progress + '%' }"
      >
        <!-- Progress text inside bar -->
        <span v-if="progress > 10" class="text-white text-sm font-bold">
          {{ Math.round(progress) }}%
        </span>
      </div>
    </div>

    <div class="mt-2 text-sm text-gray-600">
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

