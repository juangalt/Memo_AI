import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/text-input',
    name: 'TextInput',
    component: () => import('@/views/TextInput.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/overall-feedback',
    name: 'OverallFeedback',
    component: () => import('@/views/OverallFeedback.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/detailed-feedback',
    name: 'DetailedFeedback',
    component: () => import('@/views/DetailedFeedback.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/Admin.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/last-evaluation',
    name: 'LastEvaluation',
    component: () => import('@/views/LastEvaluation.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/debug',
    name: 'Debug',
    component: () => import('@/views/Debug.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/help',
    name: 'Help',
    component: () => import('@/views/Help.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

// Authentication guard
router.beforeEach(async (to, from, next) => {
  // Use the global auth store instance set up in main.ts
  const authStore = (window as any).authStoreInstance

  // If auth store is not available yet, allow navigation (will be checked again after app init)
  if (!authStore) {
    next()
    return
  }

  // Skip authentication checks for login page to avoid interference
  if (to.path === '/login') {
    // If user is already authenticated and trying to access login, redirect to home
    if (authStore.isAuthenticated) {
      next('/')
      return
    }
    // Allow access to login page
    next()
    return
  }

  // If route requires authentication or admin access
  if (to.meta.requiresAuth || to.meta.requiresAdmin) {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      // Try to validate existing session
      const valid = await authStore.validateSession()
      if (!valid) {
        // No valid session, redirect to login
        next({
          path: '/login',
          query: { redirect: to.fullPath } // Save intended destination
        })
        return
      }
    }

    // If route requires admin and user is not admin
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      // Redirect to home or show error
      next('/')
      return
    }
  }

  // Allow navigation
  next()
})

export default router

