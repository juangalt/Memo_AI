<template>
  <div style="margin-top: 2rem;">
    <h3 style="font-size: 1.25rem; font-weight: 600; color: #111827; margin-bottom: 1rem;">
      📊 Detailed Rubric Scores
    </h3>

    <div style="display: grid; gap: 1rem; grid-template-columns: 1fr;">
      <div
        v-for="[criterion, score] in Object.entries(scores)"
        :key="criterion"
        style="background-color: #f9fafb; border-radius: 0.5rem; padding: 1rem;"
      >
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
          <span
            style="padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; font-weight: 500; white-space: nowrap;"
            :style="{
              backgroundColor: score.score >= 4 ? '#dcfce7' : score.score >= 3 ? '#fef3c7' : score.score >= 2 ? '#fed7aa' : '#fee2e2',
              color: score.score >= 4 ? '#166534' : score.score >= 3 ? '#92400e' : score.score >= 2 ? '#ea580c' : '#dc2626'
            }"
          >
            {{ score.score }}/5.0
          </span>
          <h4 style="font-weight: 500; color: #111827; text-transform: capitalize; margin: 0;">
            {{ formatCriterionName(criterion) }}
          </h4>
        </div>

        <p v-if="score.justification" style="font-size: 0.875rem; color: #6b7280;">
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

