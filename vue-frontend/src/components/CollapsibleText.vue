<template>
  <div class="collapsible-text">
    <div
      ref="textContainer"
      :class="[
        'whitespace-pre-wrap transition-all duration-300 overflow-hidden',
        isExpanded ? '' : 'max-h-32'
      ]"
    >
      <slot>{{ text }}</slot>
    </div>
    
    <div
      v-if="needsCollapse"
      class="mt-2 text-center"
    >
      <button
        @click="toggleExpanded"
        class="text-blue-500 hover:text-blue-700 text-sm font-medium"
      >
        {{ isExpanded ? 'Show Less' : 'Show More' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'

interface Props {
  text?: string
  maxHeight?: number
}

const props = withDefaults(defineProps<Props>(), {
  maxHeight: 128 // 32 * 4 (32 = 8rem)
})

const textContainer = ref<HTMLElement>()
const isExpanded = ref(false)
const needsCollapse = ref(false)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const checkIfNeedsCollapse = async () => {
  await nextTick()
  if (textContainer.value) {
    const scrollHeight = textContainer.value.scrollHeight
    needsCollapse.value = scrollHeight > props.maxHeight
  }
}

onMounted(() => {
  checkIfNeedsCollapse()
})
</script>
