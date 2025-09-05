<template>
  <div class="relative inline-block text-left">
    <div>
      <button
        @click="toggleDropdown"
        class="inline-flex items-center justify-center w-full rounded-md border border-gray-300 shadow-sm px-3 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        id="language-menu-button"
        aria-expanded="true"
        aria-haspopup="true"
      >
        <span class="text-lg mr-2">{{ currentLanguageObject?.flag }}</span>
        <span class="hidden sm:inline">{{ currentLanguageObject?.name }}</span>
        <svg
          class="-mr-1 ml-2 h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd"
          />
        </svg>
      </button>
    </div>

    <!-- Dropdown menu -->
    <div
      v-if="isOpen"
      class="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
      role="menu"
      aria-orientation="vertical"
      aria-labelledby="language-menu-button"
      tabindex="-1"
    >
      <div class="py-1" role="none">
        <button
          v-for="language in availableLanguages"
          :key="language.code"
          @click="selectLanguage(language.code)"
          class="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
          :class="{ 'bg-blue-50 text-blue-700': language.code === currentLanguage }"
          role="menuitem"
        >
          <span class="text-lg mr-3">{{ language?.flag }}</span>
          <span>{{ language?.name }}</span>
          <svg
            v-if="language.code === currentLanguage"
            class="ml-auto h-5 w-5 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fill-rule="evenodd"
              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useLanguageStore } from '@/stores/language'

const languageStore = useLanguageStore()
const isOpen = ref(false)

// Computed properties from store
const currentLanguage = computed(() => languageStore.currentLanguage)
const currentLanguageObject = computed(() => languageStore.currentLanguageObject)
const availableLanguages = computed(() => languageStore.availableLanguages)

// Toggle dropdown visibility
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

// Select a language
const selectLanguage = (languageCode: string) => {
  languageStore.setLanguage(languageCode)
  isOpen.value = false
}

// Close dropdown when clicking outside
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  const menu = target.closest('.relative')
  if (!menu) {
    isOpen.value = false
  }
}

// Close dropdown on escape key
const handleEscapeKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscapeKey)
})
</script>
