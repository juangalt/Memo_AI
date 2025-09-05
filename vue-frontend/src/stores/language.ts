import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLanguageStore = defineStore('language', () => {
  // Get i18n instance from global scope (set up in main.ts)
  const getI18n = () => {
    return (window as any).$i18n || null
  }

  // Available languages
  const availableLanguages = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' }
  ]

  // Current language
  const currentLanguage = ref('en')

  // Computed property for current language object
  const currentLanguageObject = computed(() =>
    availableLanguages.find(lang => lang.code === currentLanguage.value) || availableLanguages[0]
  )

  // Initialize language from localStorage or browser detection
  const initializeLanguage = () => {
    const savedLanguage = localStorage.getItem('memo-ai-language')
    if (savedLanguage && availableLanguages.some(lang => lang.code === savedLanguage)) {
      setLanguage(savedLanguage)
    } else {
      // Auto-detect browser language
      const browserLang = navigator.language?.split('-')[0]
      if (browserLang && availableLanguages.some(lang => lang.code === browserLang)) {
        setLanguage(browserLang)
      } else {
        setLanguage('en') // Default fallback
      }
    }
  }

  // Set language
  const setLanguage = (languageCode: string) => {
    if (availableLanguages.some(lang => lang.code === languageCode)) {
      currentLanguage.value = languageCode
      const i18n = getI18n()
      if (i18n) {
        i18n.global.locale.value = languageCode
      }
      localStorage.setItem('memo-ai-language', languageCode)
    }
  }

  // Toggle between English and Spanish
  const toggleLanguage = () => {
    const newLang = currentLanguage.value === 'en' ? 'es' : 'en'
    setLanguage(newLang)
  }

  return {
    availableLanguages,
    currentLanguage,
    currentLanguageObject,
    initializeLanguage,
    setLanguage,
    toggleLanguage
  }
})
