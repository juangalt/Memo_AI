<template>
  <div class="mt-8">
    <h3 class="text-xl font-semibold text-gray-900 mb-4">
      📊 Detailed Rubric Scores
    </h3>

    <div class="grid gap-4 md:grid-cols-2">
      <div
        v-for="[criterion, score] in Object.entries(scores)"
        :key="criterion"
        class="bg-gray-50 rounded-lg p-4"
      >
        <div class="flex items-center justify-between mb-2">
          <h4 class="font-medium text-gray-900 capitalize">
            {{ formatCriterionName(criterion) }}
          </h4>
          <span
            class="px-2 py-1 rounded text-sm font-medium"
            :class="[
              score.score >= 4 ? 'bg-green-100 text-green-800' :
              score.score >= 3 ? 'bg-yellow-100 text-yellow-800' :
              score.score >= 2 ? 'bg-orange-100 text-orange-800' :
              'bg-red-100 text-red-800'
            ]"
          >
            {{ score.score }}/5.0
          </span>
        </div>

        <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div
            class="h-2 rounded-full"
            :class="[
              score.score >= 4 ? 'bg-green-500' :
              score.score >= 3 ? 'bg-yellow-500' :
              score.score >= 2 ? 'bg-orange-500' :
              'bg-red-500'
            ]"
            :style="{ width: (score.score / 5) * 100 + '%' }"
          ></div>
        </div>

        <p v-if="score.justification" class="text-sm text-gray-600">
          {{ score.justification }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  scores: Record<string, any>
}

defineProps<Props>()

const formatCriterionName = (criterion: string): string => {
  return criterion
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>

