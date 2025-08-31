<template>
  <div class="flex items-center space-x-2 text-sm">
    <span
      :class="[
        'font-medium',
        characterCount > max * 0.9 ? 'text-red-600' :
        characterCount > max * 0.8 ? 'text-yellow-600' :
        'text-gray-600'
      ]"
    >
      {{ characterCount }}/{{ max }}
    </span>

    <div class="flex-1 bg-gray-200 rounded-full h-2">
      <div
        class="h-2 rounded-full transition-all duration-300"
        :class="[
          characterCount > max * 0.9 ? 'bg-red-500' :
          characterCount > max * 0.8 ? 'bg-yellow-500' :
          'bg-blue-500'
        ]"
        :style="{ width: Math.min((characterCount / max) * 100, 100) + '%' }"
      ></div>
    </div>

    <span class="text-gray-500">
      {{ Math.max(0, max - characterCount) }} remaining
    </span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  characterCount: number
  max: number
}

defineProps<Props>()
</script>

