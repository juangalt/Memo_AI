# Vue Frontend Implementation Plan
## Memo AI Coach - Parallel Frontend Deployment

**Document ID**: vue_frontend_implementation_plan.md  
**Document Version**: 1.0  
**Created**: Phase 10 - Vue Frontend Development  
**Status**: Implementation Plan  
**Target Domain**: memo.myisland.dev/vue  

---

## Executive Summary

This document outlines the comprehensive implementation plan for creating a Vue.js frontend that will become the primary interface for Memo AI Coach at `memo.myisland.dev`. The Vue frontend will replace the existing Streamlit frontend with enhanced features and phase completion tracking.

### Key Objectives
- Create a modern, responsive Vue.js frontend with full feature parity
- Maintain complete backward compatibility with existing backend API
- **Deploy Vue frontend as the primary interface at `memo.myisland.dev`**
- Ensure compliance with all frontend specifications and requirements
- **Align with Updated Authentication Specifications** (`docs/02b_Authentication_Specifications.md`)
**✅ Authentication System Updated**: Unified login endpoint (`/api/v1/auth/login`) for all users
**✅ Legacy Admin Endpoint Removed**: No separate `/api/v1/admin/login` endpoint
**✅ Primary Deployment**: Vue frontend at root domain with phase completion tracking

### Success Criteria
- **Vue frontend accessible at `https://memo.myisland.dev/` (primary domain)**
- **Phase completion tracking displayed on homepage**
- All existing functionality replicated and working
- Performance targets met (<1s UI loads, <15s LLM responses)
- Security requirements satisfied
- Responsive design for mobile and desktop
- **Seamless transition from Streamlit to Vue interface**

---

## 📋 Implementation Guidelines

### **🔍 Human Testing Requirements**
Every implementation step **MUST** include browser-based human testing that can be performed on the VPS deployment. Each test section should include:

1. **Clear step-by-step instructions** for manual testing
2. **VPS deployment URLs** (e.g., `https://memo.myisland.dev/`)
3. **Browser developer tools usage** (console, network tab, etc.)
4. **Expected results** with ✅ checkmarks for easy verification
5. **Error scenarios** to test edge cases

### **📝 Documentation Requirements**
**ALL CHANGES MUST BE DOCUMENTED** in `vue_implementation_changelog.md` with:

- **Latest changes at the top** (reverse chronological order)
- **Date format**: `[2024-MM-DD]`
- **Status indicators**: ✅ for completed, 🔄 for in-progress, ❌ for issues
- **Detailed descriptions** of what was implemented and tested
- **Browser testing results** when applicable

### **🧪 Testing Pattern for Each Step**
```markdown
**Human Testing** (Browser):
1. ✅ **Action**: Description of what to do in browser
2. ✅ **Verification**: What to check for success
3. ✅ **Edge cases**: Test error scenarios

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step X.Y Complete: Feature Name
- Implemented feature description
- Tested functionality in browser
- Verified integration with backend API
- Status: ✅ Feature implemented and tested
```
```

### **🌐 Browser Testing Focus Areas**
- **Authentication flow**: Login, logout, session persistence
- **API communication**: Network requests, error handling
- **UI responsiveness**: Mobile/desktop compatibility
- **Route protection**: Access control and redirects
- **Error scenarios**: Network failures, invalid inputs
- **Performance**: Page load times, responsiveness

---

## Phase 1: Project Setup and Infrastructure

### Step 1.1: Create Vue Frontend Directory Structure
**Goal**: Establish the Vue frontend project structure alongside existing Streamlit frontend

**Actions**:
```bash
mkdir vue-frontend
cd vue-frontend
npm create vue@latest . -- --typescript --router --pinia --eslint --prettier
npm install axios @headlessui/vue @heroicons/vue marked date-fns
npm install -D tailwindcss autoprefixer postcss @tailwindcss/forms
```

**Test**:
```bash
cd vue-frontend
npm run dev
# Should start development server on localhost:5173
```

**Human Testing** (Browser):
1. ✅ **Open browser** to `http://localhost:5173` (or `https://memo.myisland.dev/` when deployed)
2. ✅ **Verify Vue app loads** - Should see Vue logo and "Hello Vue" text
3. ✅ **Check console** - No JavaScript errors should appear
4. ✅ **Verify responsive design** - Resize browser window, layout should adapt

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 1.1 Complete: Vue Project Setup
- Created vue-frontend directory structure
- Installed Vue 3 with TypeScript, Router, Pinia, ESLint, Prettier
- Added required dependencies: axios, UI libraries, date-fns
- Verified basic app loads in browser
- Status: ✅ Project structure established
```

### Step 1.2: Configure Build System
**Goal**: Set up production build configuration for Docker deployment

**Actions**:
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Test**:
```bash
npm run build
# Should create dist/ directory with built files
```

**Human Testing** (Browser):
1. ✅ **Run build command** and verify `dist/` directory is created
2. ✅ **Serve built files** locally: `npm install -g serve && serve dist -p 5000`
3. ✅ **Open browser** to `http://localhost:5000` (or `https://memo.myisland.dev/` when deployed)
4. ✅ **Verify production build works** - App should load without dev server
5. ✅ **Test API proxy** - Check browser network tab for API calls going to correct endpoints

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 1.2 Complete: Build System Configured
- Configured Vite build system with production settings
- Set up API proxy for development (/api → http://localhost:8000)
- Verified production build creates dist/ directory
- Tested production build serves correctly in browser
- Status: ✅ Build system configured and tested
```

### Step 1.3: Create Docker Configuration
**Goal**: Set up Docker container for Vue frontend deployment

**Actions**:
```dockerfile
# vue-frontend/Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Test**:
```bash
cd vue-frontend
docker build -t memo-ai-vue-frontend .
docker run -p 8080:80 memo-ai-vue-frontend
# Should serve Vue app on localhost:8080
```

**Human Testing** (Browser):
1. ✅ **Build Docker image** and verify it completes successfully
2. ✅ **Run container** with port mapping: `docker run -p 8080:80 memo-ai-vue-frontend`
3. ✅ **Open browser** to `http://localhost:8080` (or `https://memo.myisland.dev/` when deployed)
4. ✅ **Verify containerized app works** - Should load same as local dev server
5. ✅ **Check container logs** - `docker logs <container_id>` for any errors
6. ✅ **Test static file serving** - Refresh page, verify no issues

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 1.3 Complete: Docker Configuration Created
- Created multi-stage Dockerfile for Vue frontend
- Configured nginx for static file serving
- Built and tested Docker image locally
- Verified containerized app works in browser
- Status: ✅ Docker configuration complete and tested
```

---

## Phase 2: Docker Compose Integration

### Step 2.1: Update Docker Compose Configuration
**Goal**: Make Vue frontend the primary service at root domain with phase tracking

**Actions**:
```yaml
# Update docker-compose.yml - Replace Streamlit with Vue as primary frontend
vue-frontend:
  build: ./vue-frontend
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.vue-frontend.rule=Host(`memo.myisland.dev`)"
    - "traefik.http.routers.vue-frontend.priority=200"
    - "traefik.http.routers.vue-frontend.entrypoints=websecure"
    - "traefik.http.routers.vue-frontend.tls.certresolver=letsencrypt"
    - "traefik.http.routers.vue-frontend.middlewares=default-headers@docker,secure-headers@docker,rate-limit@docker"
    - "traefik.http.services.vue-frontend.loadbalancer.server.port=80"
  environment:
    - BACKEND_URL=http://backend:8000
    - APP_ENV=${APP_ENV:-production}
    - DEBUG_MODE=${DEBUG_MODE:-false}
    - PHASE_TRACKING_ENABLED=true
  depends_on:
    - backend
  volumes:
    - ./config:/app/config:ro
    - ./logs:/app/logs
    - ./vue_implementation_changelog.md:/app/changelog.md:ro
  user: "1000:1000"
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:80/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

**Test**:
```bash
docker compose up -d vue-frontend
docker compose ps
# Should show vue-frontend service running at root domain
```

**Human Testing** (Browser):
1. ✅ **Start Vue frontend service**: `docker compose up -d vue-frontend`
2. ✅ **Check service status**: `docker compose ps` - should show "Up" status
3. ✅ **Access primary domain**: Open browser to `https://memo.myisland.dev/` (VPS deployment)
4. ✅ **Verify phase tracking**: Check homepage displays current implementation phases
5. ✅ **Test routing**: Confirm Vue frontend loads directly at root domain
6. ✅ **Check Traefik dashboard**: Access `https://memo.myisland.dev/dashboard` to verify routing

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 2.1 Complete: Docker Compose Integration
- Configured Vue frontend as primary service at root domain
- Set up phase tracking with changelog integration
- Mounted vue_implementation_changelog.md for homepage display
- Verified primary domain routing works correctly in browser
- Status: ✅ Vue frontend deployed as primary interface
```

### Step 2.2: Create Phase Tracking Component
**Goal**: Implement homepage component that displays implementation progress

**Actions**:
```vue
<!-- src/views/Home.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="text-center">
          <h1 class="text-4xl font-bold text-gray-900 mb-2">
            📝 Memo AI Coach
          </h1>
          <p class="text-lg text-gray-600">
            Vue Frontend Implementation Progress
          </p>
        </div>
      </div>
    </header>

    <!-- Phase Progress -->
    <main class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">
          🚀 Implementation Phases
        </h2>

        <!-- Phase Progress Cards -->
        <div class="space-y-4" v-if="phases.length > 0">
          <div
            v-for="phase in phases"
            :key="phase.id"
            class="border rounded-lg p-4"
            :class="phase.status === 'completed' ? 'border-green-200 bg-green-50' :
                     phase.status === 'in-progress' ? 'border-blue-200 bg-blue-50' :
                     'border-gray-200 bg-gray-50'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <span class="text-2xl">{{ phase.emoji }}</span>
                <div>
                  <h3 class="font-semibold text-gray-900">{{ phase.title }}</h3>
                  <p class="text-sm text-gray-600">{{ phase.description }}</p>
                </div>
              </div>
              <span
                class="px-3 py-1 rounded-full text-sm font-medium"
                :class="phase.status === 'completed' ? 'bg-green-100 text-green-800' :
                         phase.status === 'in-progress' ? 'bg-blue-100 text-blue-800' :
                         'bg-gray-100 text-gray-800'"
              >
                {{ phase.statusText }}
              </span>
            </div>

            <!-- Progress bar for in-progress phases -->
            <div v-if="phase.status === 'in-progress' && phase.progress" class="mt-3">
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  :style="{ width: phase.progress + '%' }"
                ></div>
              </div>
              <p class="text-xs text-gray-500 mt-1">{{ phase.progress }}% complete</p>
            </div>

            <!-- Completion date -->
            <div v-if="phase.completedDate" class="mt-2 text-xs text-gray-500">
              ✅ Completed on {{ formatDate(phase.completedDate) }}
            </div>
          </div>
        </div>

        <!-- Get Started Button -->
        <div class="mt-8 text-center" v-if="hasIncompletePhases">
          <router-link
            to="/login"
            class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔑 Login to Access Features
          </router-link>
          <p class="text-sm text-gray-600 mt-2">
            Some features may not be available until implementation is complete
          </p>
        </div>

        <!-- All Complete Message -->
        <div v-else class="mt-8 text-center">
          <div class="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-green-800 mb-2">
              🎉 Implementation Complete!
            </h3>
            <p class="text-green-700">
              All phases have been successfully implemented. The Vue frontend is now fully operational.
            </p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// Phase data structure
const phases = ref([
  {
    id: 'phase1',
    title: 'Phase 1: Project Setup',
    description: 'Vue project structure, build system, and Docker configuration',
    emoji: '🏗️',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-15',
    progress: null
  },
  {
    id: 'phase2',
    title: 'Phase 2: Infrastructure',
    description: 'Docker Compose integration and production deployment',
    emoji: '🐳',
    status: 'completed',
    statusText: 'Completed',
    completedDate: '2024-01-16',
    progress: null
  },
  {
    id: 'phase3',
    title: 'Phase 3: Core Application',
    description: 'Vue Router, authentication store, and app structure',
    emoji: '⚛️',
    status: 'in-progress',
    statusText: 'In Progress',
    completedDate: null,
    progress: 75
  },
  {
    id: 'phase4',
    title: 'Phase 4: API Integration',
    description: 'API client service and backend communication',
    emoji: '🔌',
    status: 'pending',
    statusText: 'Pending',
    completedDate: null,
    progress: null
  },
  {
    id: 'phase5',
    title: 'Phase 5: UI Components',
    description: 'Core UI components and responsive design',
    emoji: '🎨',
    status: 'pending',
    statusText: 'Pending',
    completedDate: null,
    progress: null
  }
])

const hasIncompletePhases = computed(() =>
  phases.value.some(phase => phase.status !== 'completed')
)

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

// Load phase status from changelog file (mounted to container)
onMounted(async () => {
  try {
    // This would load from the mounted changelog file
    // For now, using static data - will be updated dynamically
    console.log('Phase tracking initialized')
  } catch (error) {
    console.error('Failed to load phase status:', error)
  }
})
</script>
```

**Test**:
```bash
# Test homepage component renders
npm run dev
# Homepage should display phase tracking cards
```

**Human Testing** (Browser):
1. ✅ **Open homepage**: Navigate to `https://memo.myisland.dev/` (VPS deployment)
2. ✅ **Verify phase display**: Check that all implementation phases are shown with status
3. ✅ **Test progress bars**: Confirm in-progress phases show progress indicators
4. ✅ **Check completion dates**: Verify completed phases show completion dates
5. ✅ **Test login button**: Click login button and verify navigation to login page
6. ✅ **Verify responsive design**: Test on mobile and desktop viewports

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 2.2 Complete: Phase Tracking Component
- Created homepage component with phase progress display
- Implemented status tracking (completed, in-progress, pending)
- Added progress bars for active phases
- Integrated login navigation for accessing features
- Status: ✅ Phase tracking homepage implemented
```

---

## Phase 3: Core Application Structure

### Step 3.1: Set Up Vue Router
**Goal**: Configure routing for primary domain with homepage and protected routes

**Actions**:
```javascript
// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'Home', component: () => import('@/views/Home.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/Login.vue') },
  { path: '/text-input', name: 'TextInput', component: () => import('@/views/TextInput.vue'), meta: { requiresAuth: true } },
  { path: '/overall-feedback', name: 'OverallFeedback', component: () => import('@/views/OverallFeedback.vue'), meta: { requiresAuth: true } },
  { path: '/detailed-feedback', name: 'DetailedFeedback', component: () => import('@/views/DetailedFeedback.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('@/views/Admin.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/debug', name: 'Debug', component: () => import('@/views/Debug.vue'), meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Validate session on protected routes
  if (to.meta.requiresAuth || to.meta.requiresAdmin) {
    if (!authStore.isAuthenticated) {
      // Try to validate existing session
      const valid = await authStore.validateSession()
      if (!valid) {
        next('/login')
        return
      }
    }

    if (to.meta.requiresAdmin && !authStore.isAdmin) {
      next('/admin')
      return
    }
  }

  next()
})

export default router
```

**Test**:
```bash
npm run dev
# Navigate to http://localhost:3000/
# Should display homepage with phase tracking
```

**Human Testing** (Browser):
1. ✅ **Start dev server**: `npm run dev`
2. ✅ **Navigate to base URL**: Open browser to `http://localhost:3000/` (or `https://memo.myisland.dev/` when deployed)
3. ✅ **Verify homepage**: Should display phase tracking cards and progress
4. ✅ **Test route protection**: Try accessing `/text-input` directly - should redirect to login
5. ✅ **Check browser URL**: Verify URL changes correctly during navigation
6. ✅ **Test browser back/forward**: Use browser navigation buttons to test routing

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 3.1 Complete: Vue Router Configured
- Set up Vue Router with tab-based navigation structure
- Configured route guards for authentication and admin access
- Implemented automatic redirects and session validation
- Tested route protection and navigation flow in browser
- Status: ✅ Vue Router configured and tested
```

### Step 3.1.1: Create App Entry Point with Session Initialization
**Goal**: Set up Vue app with automatic session validation on startup

**Actions**:
```javascript
// src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize authentication store globally for API client access
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
window.authStoreInstance = authStore

// Initialize session validation on app startup
// Note: Per auth specs, tokens are stored in memory only
authStore.initializeFromMemory()

// Try to validate existing session on app load
authStore.validateSession().catch(() => {
  // Session validation failed, user will be redirected to login if needed
  console.log('No valid session found, proceeding to login')
})

app.mount('#app')
```

**Test**:
```bash
# Start the app with existing session token
# Should automatically validate session and redirect appropriately
```

**Human Testing** (Browser):
1. ✅ **Start the application**: Open browser to `https://memo.myisland.dev/` (VPS deployment)
2. ✅ **Check initial load**: App should load and attempt session validation
3. ✅ **Monitor network tab**: Verify API call to `/api/v1/auth/validate` on startup
4. ✅ **Test without session**: Clear browser data and reload - should redirect to login
5. ✅ **Test with valid session**: Login first, then reload page - should stay logged in
6. ✅ **Check console logs**: Verify session validation messages appear in console

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 3.1.1 Complete: App Entry Point Configured
- Set up Vue app with Pinia store initialization
- Implemented automatic session validation on startup
- Configured global auth store access for API client
- Tested session initialization and validation flow in browser
- Status: ✅ App entry point configured and tested
```

### Step 3.2: Create Authentication Store
**Goal**: Implement authentication state management

**Actions**:
```javascript
// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  // Store token in memory only (never localStorage per auth specs)
  const sessionToken = ref(null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const username = computed(() => user.value?.username || '')

  const login = async (username, password) => {
    isLoading.value = true
    try {
      const result = await authService.login(username, password)
      if (result.success) {
        user.value = result.data.user || result.data
        sessionToken.value = result.data.session_token
        return { success: true }
      }
      // Handle standardized error format from auth specs
      if (result.data?.errors && result.data.errors.length > 0) {
        const error = result.data.errors[0]
        return { success: false, error: error.message, code: error.code }
      }
      return { success: false, error: result.error || 'Login failed' }
    } catch (error) {
      return { success: false, error: error.message || 'Login failed' }
    } finally {
      isLoading.value = false
    }
  }

  const validateSession = async () => {
    if (!sessionToken.value) return false

    try {
      const result = await authService.validateSession()
      if (result.success) {
        user.value = result.data.user || result.data
        return true
      }
      // Handle auth spec error codes
      if (result.data?.errors && result.data.errors.length > 0) {
        const error = result.data.errors[0]
        if (error.code === 'AUTH_SESSION_EXPIRED' || error.code === 'AUTH_INVALID_TOKEN') {
          logout()
          return false
        }
      }
      return false
    } catch (error) {
      logout()
      return false
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      sessionToken.value = null
    }
  }

  // Initialize from memory if available (not localStorage)
  const initializeFromMemory = () => {
    // Token should be passed from previous session or login
    // Per auth specs: store in memory only, never persistent storage
  }

  return {
    user, sessionToken, isLoading,
    isAuthenticated, isAdmin, username,
    login, validateSession, logout, initializeFromMemory
  }
})
```

**Test**:
```bash
# In browser console:
import { useAuthStore } from '@/stores/auth'
const auth = useAuthStore()
console.log(auth.isAuthenticated) // Should be false initially
```

**Human Testing** (Browser):
1. ✅ **Open browser console**: Navigate to `https://memo.myisland.dev/`
2. ✅ **Test initial state**: Check `auth.isAuthenticated` should be `false`
3. ✅ **Test login flow**: Enter valid credentials and verify login success
4. ✅ **Check session persistence**: Refresh page and verify user stays logged in
5. ✅ **Test logout**: Click logout and verify user is redirected to login
6. ✅ **Test error handling**: Try invalid credentials and check error messages

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 3.2 Complete: Authentication Store Created
- Implemented Pinia authentication store with unified login endpoint
- Set up memory-only token storage per auth specs
- Configured standardized error handling for auth spec error codes
- Tested authentication flow and session management in browser
- Status: ✅ Authentication store implemented and tested
```

---

## Phase 4: API Service Layer

### Step 4.1: Create API Client Service
**Goal**: Implement API communication layer

**Actions**:
```javascript
// src/services/api.js
import axios from 'axios'

class APIClient {
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Memo-AI-Coach-Vue/1.0.0'
      }
    })
    
    this.client.interceptors.request.use(
      (config) => {
        // Get token from auth store (memory only, per auth specs)
        const authStore = window.authStoreInstance
        const token = authStore?.sessionToken || null
        if (token) {
          config.headers['X-Session-Token'] = token
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Clear session on auth errors per auth specs
          const authStore = window.authStoreInstance
          if (authStore) {
            authStore.logout()
          }
          window.location.href = '/vue/login'
        }
        return Promise.reject(error)
      }
    )
  }
  
  async request(method, endpoint, data = null, config = {}) {
    try {
      const response = await this.client.request({
        method, url: endpoint, data, ...config
      })
      return { success: true, data: response.data, status: response.status }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || error.message,
        status: error.response?.status
      }
    }
  }
  
  get(endpoint, config = {}) { return this.request('GET', endpoint, null, config) }
  post(endpoint, data = null, config = {}) { return this.request('POST', endpoint, data, config) }
  put(endpoint, data = null, config = {}) { return this.request('PUT', endpoint, data, config) }
  delete(endpoint, config = {}) { return this.request('DELETE', endpoint, null, config) }
}

export const apiClient = new APIClient()
```

**Test**:
```bash
# Test API client:
import { apiClient } from '@/services/api'
apiClient.get('/health').then(console.log)
```

**Human Testing** (Browser):
1. ✅ **Open browser console**: Navigate to `https://memo.myisland.dev/`
2. ✅ **Test health endpoint**: Run `apiClient.get('/health').then(console.log)` in console
3. ✅ **Verify API calls**: Check network tab for requests to `https://memo.myisland.dev/api/health`
4. ✅ **Test authentication headers**: Login first, then check that `X-Session-Token` header is sent
5. ✅ **Test error handling**: Try invalid endpoint and verify error response
6. ✅ **Monitor CORS**: Ensure no CORS errors in console

**Document Changes**: Update `vue_implementation_changelog.md` with:
```
## [2024-XX-XX] Step 4.1 Complete: API Client Service Created
- Implemented Axios-based API client with unified authentication
- Set up automatic X-Session-Token header injection
- Configured standardized error handling and response processing
- Tested API communication and authentication headers in browser
- Status: ✅ API client service implemented and tested
```

### Step 4.2: Create Authentication Service
**Goal**: Implement unified authentication API calls

**Actions**:
```javascript
// src/services/auth.js
import { apiClient } from './api'

export const authService = {
  async login(username, password) {
    return apiClient.post('/api/v1/auth/login', { username, password })
  },

  async validateSession() {
    return apiClient.get('/api/v1/auth/validate')
  },

  async logout() {
    return apiClient.post('/api/v1/auth/logout')
  },

  // Admin-specific endpoints
  async listUsers() {
    return apiClient.get('/api/v1/admin/users')
  },

  async createUser(userData) {
    return apiClient.post('/api/v1/admin/users/create', userData)
  },

  async deleteUser(username) {
    return apiClient.delete(`/api/v1/admin/users/${username}`)
  },

  async getConfig(configName) {
    return apiClient.get(`/api/v1/admin/config/${configName}`)
  },

  async updateConfig(configName, content) {
    return apiClient.put(`/api/v1/admin/config/${configName}`, { content })
  }
}
```

**Test**:
```bash
# Test authentication service:
import { authService } from '@/services/auth'
authService.login('test', 'password').then(console.log)
```

### Step 4.3: Create Evaluation Service
**Goal**: Implement evaluation API calls with proper response format handling

**Actions**:
```javascript
// src/services/evaluation.js
import { apiClient } from './api'

export const evaluationService = {
  async submitEvaluation(textContent) {
    const result = await apiClient.post('/api/v1/evaluations/submit', {
      text_content: textContent
    })

    if (result.success) {
      // Handle standardized response format
      const { data, meta, errors } = result.data

      if (errors && errors.length > 0) {
        return {
          success: false,
          error: errors[0].message,
          status: errors[0].code
        }
      }

      return {
        success: true,
        data: data,
        meta: meta
      }
    }

    return result
  },

  async getEvaluation(evaluationId) {
    const result = await apiClient.get(`/api/v1/evaluations/${evaluationId}`)

    if (result.success) {
      const { data, meta, errors } = result.data
      return {
        success: true,
        data: data,
        meta: meta,
        errors: errors
      }
    }

    return result
  }
}
```

**Test**:
```bash
# Test evaluation service:
import { evaluationService } from '@/services/evaluation'
evaluationService.submitEvaluation('Sample text').then(console.log)
```

**Success Criteria**: Evaluation service handles API calls with proper response format processing

---

## Phase 5: Core UI Components

### Step 5.1: Create Login Component
**Goal**: Implement centralized authentication interface

**Actions**:
```vue
<!-- src/views/Login.vue -->
<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          📝 Memo AI Coach
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Intelligent text evaluation and feedback system
        </p>
      </div>
      
      <div class="bg-white py-8 px-6 shadow rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-6">🔐 Authentication Required</h3>
        
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your username"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your password"
            />
          </div>
          
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <span v-if="isLoading">Loading...</span>
              <span v-else>🔑 Login</span>
            </button>
          </div>
        </form>
        
        <div v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const isLoading = ref(false)
const error = ref('')

  const handleLogin = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const result = await authStore.login(form.value.username, form.value.password)

      if (result.success) {
        router.push('/text-input')
      } else {
        // Handle auth spec error codes
        if (result.code === 'AUTH_ACCOUNT_LOCKED') {
          error.value = 'Account temporarily locked due to multiple failed attempts. Please try again later.'
        } else if (result.code === 'AUTH_INVALID_CREDENTIALS') {
          error.value = 'Invalid username or password.'
        } else {
          error.value = result.error || 'Login failed. Please try again.'
        }
      }
    } catch (err) {
      error.value = 'Login failed. Please try again.'
    } finally {
      isLoading.value = false
    }
  }
</script>
```

**Test**:
```bash
# Navigate to http://localhost:3000/vue/login
# Should display login form
# Test with valid/invalid credentials
```

### Step 5.2: Create Main Layout Component
**Goal**: Implement tabbed navigation interface

**Actions**:
```vue
<!-- src/components/Layout.vue -->
<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">📝 Memo AI Coach</h1>
          </div>
          
          <div class="flex items-center space-x-4">
            <AuthStatus />
            <button @click="handleLogout" class="text-sm text-gray-500 hover:text-gray-700">
              Logout
            </button>
          </div>
        </div>
        
        <nav class="flex space-x-8">
          <router-link
            v-for="tab in tabs"
            :key="tab.name"
            :to="tab.path"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm',
              $route.path === tab.path
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ tab.name }}
          </router-link>
        </nav>
      </div>
    </header>
    
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AuthStatus from './AuthStatus.vue'

const router = useRouter()
const authStore = useAuthStore()

const tabs = computed(() => {
  const baseTabs = [
    { name: 'Text Input', path: '/text-input' },
    { name: 'Overall Feedback', path: '/overall-feedback' },
    { name: 'Detailed Feedback', path: '/detailed-feedback' }
  ]
  
  if (authStore.isAdmin) {
    baseTabs.push(
      { name: 'Admin', path: '/admin' },
      { name: 'Debug', path: '/debug' }
    )
  }
  
  return baseTabs
})

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
```

**Test**:
```bash
# After login, verify tab navigation works
# Check admin tabs appear for admin users
# Verify logout functionality
```

---

## Phase 6: Core Functionality Implementation

### Step 6.1: Create Text Input Component
**Goal**: Implement text submission functionality

**Actions**:
```vue
<!-- src/views/TextInput.vue -->
<template>
  <Layout>
    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Submit Text for Evaluation
        </h1>
        
        <p class="text-gray-600 mb-6">
          Enter your text below for comprehensive AI-powered evaluation and feedback.
        </p>
        
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Text to Evaluate
          </label>
          <textarea
            v-model="textContent"
            :maxlength="10000"
            rows="12"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter your text here (maximum 10,000 characters)..."
          />
          
          <div class="flex justify-between items-center mt-2">
            <span class="text-sm text-gray-500">
              {{ characterCount }}/10,000 characters
            </span>
            <CharacterCounter :count="characterCount" :max="10000" />
          </div>
        </div>
        
        <div class="flex justify-center">
          <button
            @click="submitEvaluation"
            :disabled="!canSubmit || isSubmitting"
            class="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting">🤖 AI is evaluating your text...</span>
            <span v-else>🚀 Submit for Evaluation</span>
          </button>
        </div>
        
        <ProgressBar v-if="isSubmitting" :progress="progress" :status="status" />
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useEvaluationStore } from '@/stores/evaluation'
import Layout from '@/components/Layout.vue'
import CharacterCounter from '@/components/CharacterCounter.vue'
import ProgressBar from '@/components/ProgressBar.vue'

const router = useRouter()
const evaluationStore = useEvaluationStore()

const textContent = ref('')
const isSubmitting = ref(false)
const progress = ref(0)
const status = ref('')

const characterCount = computed(() => textContent.value.length)
const canSubmit = computed(() => 
  textContent.value.trim().length > 0 && 
  characterCount.value <= 10000
)

const submitEvaluation = async () => {
  if (!canSubmit.value) return
  
  isSubmitting.value = true
  progress.value = 0
  status.value = '📝 Analyzing text structure...'
  
  try {
    const progressInterval = setInterval(() => {
      progress.value += 1
      if (progress.value <= 30) {
        status.value = '📝 Analyzing text structure...'
      } else if (progress.value <= 60) {
        status.value = '🧠 Processing content with AI...'
      } else if (progress.value <= 90) {
        status.value = '📊 Generating detailed feedback...'
      } else {
        status.value = '✅ Finalizing evaluation...'
      }
    }, 50)
    
    const result = await evaluationStore.submitEvaluation(textContent.value)
    
    clearInterval(progressInterval)
    progress.value = 100
    
    if (result) {
      router.push('/overall-feedback')
    }
  } catch (error) {
    console.error('Evaluation failed:', error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
```

**Test**:
```bash
# Navigate to text input page
# Enter text and submit
# Verify progress indicator works
# Check redirect to overall feedback on success
```

### Step 6.2: Create Evaluation Store
**Goal**: Implement evaluation state management

**Actions**:
```javascript
// src/stores/evaluation.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { evaluationService } from '@/services/evaluation'

export const useEvaluationStore = defineStore('evaluation', () => {
  const currentEvaluation = ref(null)
  const evaluationHistory = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  
  const hasEvaluation = computed(() => !!currentEvaluation.value)
  const hasHistory = computed(() => evaluationHistory.value.length > 0)
  
  const submitEvaluation = async (textContent) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await evaluationService.submitEvaluation(textContent)
      if (result.success) {
        // Handle corrected response format from evaluation service
        currentEvaluation.value = result.data.evaluation
        evaluationHistory.value.unshift(result.data.evaluation)
        return result.data.evaluation
      } else {
        error.value = result.error
        return null
      }
    } catch (err) {
      error.value = err.message
      return null
    } finally {
      isLoading.value = false
    }
  }
  
  const clearEvaluation = () => {
    currentEvaluation.value = null
    error.value = null
  }
  
  return {
    currentEvaluation,
    evaluationHistory,
    isLoading,
    error,
    hasEvaluation,
    hasHistory,
    submitEvaluation,
    clearEvaluation
  }
})
```

**Test**:
```bash
# Test evaluation store:
import { useEvaluationStore } from '@/stores/evaluation'
const evalStore = useEvaluationStore()
console.log(evalStore.hasEvaluation) // Should be false initially
```

---

## Phase 7: Feedback Display Components

### Step 7.1: Create Overall Feedback Component
**Goal**: Display evaluation results with scores and feedback

**Actions**:
```vue
<!-- src/views/OverallFeedback.vue -->
<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Overall Feedback
        </h1>
        
        <div v-if="evaluation" class="space-y-8">
          <div class="text-center">
            <div class="bg-blue-50 rounded-lg p-8 border-l-4 border-blue-500">
              <h2 class="text-2xl font-semibold text-gray-700 mb-2">
                Overall Score
              </h2>
              <div class="text-6xl font-bold text-blue-600">
                {{ overallScore }}/5.0
              </div>
            </div>
          </div>
          
          <div class="grid md:grid-cols-2 gap-6">
            <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                💪 Strengths
              </h3>
              <ul v-if="strengths.length" class="space-y-2">
                <li v-for="strength in strengths" :key="strength" class="flex items-start">
                  <span class="text-green-500 mr-2">•</span>
                  <span>{{ strength }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600">No specific strengths identified</p>
            </div>
            
            <div class="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
              <h3 class="text-xl font-semibold text-gray-900 mb-4">
                🎯 Opportunities for Improvement
              </h3>
              <ul v-if="opportunities.length" class="space-y-2">
                <li v-for="opportunity in opportunities" :key="opportunity" class="flex items-start">
                  <span class="text-yellow-500 mr-2">•</span>
                  <span>{{ opportunity }}</span>
                </li>
              </ul>
              <p v-else class="text-gray-600">No improvement opportunities identified</p>
            </div>
          </div>
          
          <RubricScores :scores="rubricScores" />
          
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="flex justify-between text-sm text-gray-600">
              <span>Processing Time: {{ processingTime }}s</span>
              <span>Created: {{ formatDate(createdAt) }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="text-center py-12">
          <div class="text-gray-500">
            <p class="text-lg mb-4">📝 Submit text for evaluation to see overall feedback</p>
            <router-link 
              to="/text-input"
              class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Text Input
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import { computed } from 'vue'
import { useEvaluationStore } from '@/stores/evaluation'
import Layout from '@/components/Layout.vue'
import RubricScores from '@/components/RubricScores.vue'
import { formatDate } from '@/utils/formatters'

const evaluationStore = useEvaluationStore()

const evaluation = computed(() => evaluationStore.currentEvaluation)
const overallScore = computed(() => evaluation.value?.overall_score || 0)
const strengths = computed(() => evaluation.value?.strengths || [])
const opportunities = computed(() => evaluation.value?.opportunities || [])
const rubricScores = computed(() => evaluation.value?.rubric_scores || {})
const processingTime = computed(() => evaluation.value?.processing_time || 0)
const createdAt = computed(() => evaluation.value?.created_at || new Date())
</script>
```

**Test**:
```bash
# Submit text for evaluation
# Navigate to overall feedback
# Verify score, strengths, and opportunities display correctly
```

---

## Phase 8: Admin and Debug Components

### Step 8.1: Create Admin Component
**Goal**: Implement admin panel with configuration management

**Actions**:
```vue
<!-- src/views/Admin.vue -->
<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Admin Panel
        </h1>
        
        <div class="grid md:grid-cols-2 gap-6">
          <div class="bg-blue-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🏥 Health Monitoring
            </h3>
            <HealthStatus />
          </div>
          
          <div class="bg-green-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              ⚙️ Configuration Management
            </h3>
            <ConfigEditor />
          </div>
          
          <div class="bg-yellow-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              👥 User Management
            </h3>
            <UserManagement />
          </div>
          
          <div class="bg-purple-50 rounded-lg p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🔗 Session Management
            </h3>
            <SessionManagement />
          </div>
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup>
import Layout from '@/components/Layout.vue'
import HealthStatus from '@/components/admin/HealthStatus.vue'
import ConfigEditor from '@/components/admin/ConfigEditor.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import SessionManagement from '@/components/admin/SessionManagement.vue'
</script>
```

**Test**:
```bash
# Login as admin user
# Navigate to admin panel
# Verify all admin components load
# Test health monitoring
# Test configuration editing
```

### Step 8.2: Create Error Handling Components
**Goal**: Implement comprehensive error handling and user feedback

**Actions**:
```vue
<!-- src/components/common/Alert.vue -->
<template>
  <div v-if="show" class="fixed top-4 right-4 z-50 max-w-sm">
    <div :class="alertClass" class="rounded-lg p-4 shadow-lg">
      <div class="flex items-center">
        <div class="flex-1">
          <p class="text-sm font-medium">{{ message }}</p>
          <p v-if="details" class="text-sm opacity-90">{{ details }}</p>
        </div>
        <button @click="$emit('close')" class="ml-3">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

defineProps({
  show: Boolean,
  message: String,
  details: String,
  type: {
    type: String,
    default: 'error'
  }
})

defineEmits(['close'])

const alertClass = computed(() => {
  const base = 'bg-white border-l-4'
  switch (props.type) {
    case 'success': return `${base} border-green-500 text-green-700`
    case 'warning': return `${base} border-yellow-500 text-yellow-700`
    case 'error': return `${base} border-red-500 text-red-700`
    default: return `${base} border-blue-500 text-blue-700`
  }
})
</script>
```

```javascript
// src/stores/alert.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref([])

  const showAlert = (message, type = 'info', duration = 5000) => {
    const id = Date.now()
    alerts.value.push({ id, message, type, show: true })

    if (duration > 0) {
      setTimeout(() => {
        hideAlert(id)
      }, duration)
    }

    return id
  }

  const hideAlert = (id) => {
    const alert = alerts.value.find(a => a.id === id)
    if (alert) {
      alert.show = false
      setTimeout(() => {
        alerts.value = alerts.value.filter(a => a.id !== id)
      }, 300)
    }
  }

  const showSuccess = (message) => showAlert(message, 'success')
  const showError = (message) => showAlert(message, 'error')
  const showWarning = (message) => showAlert(message, 'warning')
  const showInfo = (message) => showAlert(message, 'info')

  return {
    alerts,
    showAlert,
    hideAlert,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
})
```

**Test**:
```bash
# Test error handling:
import { useAlertStore } from '@/stores/alert'
const alertStore = useAlertStore()
alertStore.showError('Test error message')
# Should display error alert
```

### Step 8.3: Create Loading and Progress Components
**Goal**: Implement loading states and progress indicators

**Actions**:
```vue
<!-- src/components/common/Loading.vue -->
<template>
  <div class="flex items-center justify-center">
    <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
    <span v-if="text" class="ml-2 text-sm text-gray-600">{{ text }}</span>
  </div>
</template>

<script setup>
defineProps({
  text: String
})
</script>
```

```vue
<!-- src/components/common/ProgressBar.vue -->
<template>
  <div class="w-full bg-gray-200 rounded-full h-2">
    <div
      :class="progressClass"
      :style="{ width: progress + '%' }"
      class="h-2 rounded-full transition-all duration-300"
    ></div>
  </div>
  <p v-if="status" class="text-sm text-gray-600 mt-2">{{ status }}</p>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  progress: Number,
  status: String
})

const progressClass = computed(() => {
  if (props.progress < 30) return 'bg-blue-500'
  if (props.progress < 70) return 'bg-yellow-500'
  return 'bg-green-500'
})
</script>
```

**Test**:
```bash
# Test loading components during evaluation submission
# Should show progress bar and status updates
```

---

## Phase 9: Production Deployment

### Step 9.1: Environment Configuration
**Goal**: Set up production environment variables

**Actions**:
```bash
# Create .env.production file
VITE_BACKEND_URL=https://mateo.myisland.dev/api
VITE_APP_ENV=production
VITE_DEBUG_MODE=false
```

**Test**:
```bash
npm run build
# Verify build completes without errors
```

### Step 9.2: Deploy to Production
**Goal**: Deploy Vue frontend to memo.myisland.dev/vue

**Actions**:
```bash
# Build and deploy
docker compose build vue-frontend
docker compose up -d vue-frontend

# Verify deployment
docker compose ps
curl -f https://memo.myisland.dev/health
```

**Test**:
```bash
# Access https://memo.myisland.dev/
# Verify Vue frontend loads
# Test authentication flow
# Verify all functionality works
# Compare with existing Streamlit frontend at https://memo.myisland.dev/
```

---

## Phase 10: Testing and Validation

### Step 10.1: Functional Testing
**Goal**: Verify all functionality matches existing frontend

**Test Cases**:
1. **Authentication**: Login/logout for both users and admins
2. **Text Submission**: Submit text and receive evaluation
3. **Feedback Display**: View overall and detailed feedback
4. **Admin Functions**: Configuration editing, user management
5. **Session Management**: Session persistence and cleanup
6. **Error Handling**: Network errors, validation errors
7. **Responsive Design**: Mobile and desktop compatibility

**Test Script**:
```bash
# Automated testing script
npm run test:e2e
# Should run comprehensive test suite
```

### Step 10.2: Performance Testing
**Goal**: Ensure performance meets requirements

**Tests**:
```bash
# Load testing
ab -n 100 -c 10 https://memo.myisland.dev/

# Performance monitoring
# Verify <1 second UI loads
# Verify <15 second LLM responses
```

### Step 10.3: Security Testing
**Goal**: Verify security compliance

**Tests**:
1. **Authentication**: Verify proper session management
2. **Authorization**: Test admin-only access controls
3. **Input Validation**: Test XSS and injection prevention
4. **HTTPS**: Verify SSL/TLS configuration
5. **CORS**: Test cross-origin request handling

---

## Phase 11: Documentation and Handover

### Step 11.1: Update Documentation
**Goal**: Document Vue frontend implementation

**Actions**:
1. Update architecture documentation
2. Create Vue frontend user guide
3. Document deployment procedures
4. Create troubleshooting guide

### Step 11.2: Create Migration Plan
**Goal**: Plan eventual deprecation of Streamlit frontend

**Actions**:
1. Monitor usage statistics
2. Gather user feedback
3. Plan feature parity validation
4. Create deprecation timeline

---

## Risk Assessment and Mitigation

### Technical Risks
1. **API Compatibility**: Ensure Vue frontend works with existing backend
   - **Mitigation**: Comprehensive API testing and validation
2. **Performance Issues**: Vue frontend may be slower than Streamlit
   - **Mitigation**: Performance optimization and monitoring
3. **Browser Compatibility**: Vue may not work in older browsers
   - **Mitigation**: Modern browser targeting and polyfills

### Operational Risks
1. **User Adoption**: Users may prefer existing Streamlit interface
   - **Mitigation**: Parallel deployment allows gradual migration
2. **Maintenance Overhead**: Two frontends require more maintenance
   - **Mitigation**: Clear documentation and automated testing
3. **Deployment Complexity**: More complex deployment process
   - **Mitigation**: Automated deployment scripts and monitoring

---

## Success Metrics

### Technical Metrics
- **Performance**: <1s UI loads, <15s LLM responses
- **Reliability**: 99.9% uptime
- **Security**: Zero security vulnerabilities
- **Compatibility**: 100% API compatibility

### User Experience Metrics
- **Usability**: Improved user satisfaction scores
- **Accessibility**: WCAG AA compliance
- **Responsiveness**: Mobile-friendly design
- **Feature Parity**: 100% functionality match

### Business Metrics
- **Adoption**: User migration to Vue frontend
- **Maintenance**: Reduced maintenance overhead
- **Scalability**: Support for increased user load
- **Future-Proofing**: Modern technology stack

---

## Summary of Corrections Made

### **Key Fixes Applied Based on Updated Auth Specifications:**

#### **1. Authentication System Alignment**
- ✅ **Unified Login Endpoint** - Uses `/api/v1/auth/login` for all users (legacy `/api/v1/admin/login` removed)
- ✅ **Session Validation** - Implements `/api/v1/auth/validate` endpoint per auth specs
- ✅ **Memory-Only Token Storage** - Removed localStorage usage per auth spec requirements
- ✅ **Standardized Error Handling** - Implements auth spec error codes and messages
- ✅ **Legacy Admin Endpoint Removal** - Completely removed separate admin login endpoint from specifications

#### **2. API Integration Corrections**
- ✅ **Proper Header Usage** - `X-Session-Token` header for all authenticated requests
- ✅ **Standardized Response Format** - Handles `{data: {}, meta: {}, errors: []}` format
- ✅ **Error Code Processing** - Specific handling for `AUTH_INVALID_CREDENTIALS`, `AUTH_ACCOUNT_LOCKED`, etc.

#### **3. Session Management Updates**
- ✅ **Automatic Session Validation** - Router guards validate sessions on protected routes
- ✅ **Proper Session Cleanup** - Clears tokens on logout/expiration per auth specs
- ✅ **Global Auth Store Access** - API client can access tokens from memory store

#### **4. User Experience Improvements**
- ✅ **Auth-Specific Error Messages** - Clear feedback for different auth error scenarios
- ✅ **Session Expiration Handling** - Automatic logout on expired sessions
- ✅ **Brute Force Protection UI** - Handles account lockout scenarios gracefully

#### **5. Security Compliance**
- ✅ **No Persistent Token Storage** - Tokens stored in memory only per auth specs
- ✅ **Secure Logout Process** - Proper session cleanup on logout
- ✅ **Role-Based Route Protection** - Admin routes properly protected

### **Updated Architecture Overview:**

```
Vue Frontend (/vue)          Backend API (per Auth Specs)
├── Login → POST /api/v1/auth/login (unified endpoint)
├── Session Validation → GET /api/v1/auth/validate
├── Logout → POST /api/v1/auth/logout
├── Text Evaluation → POST /api/v1/evaluations/submit
├── Admin Functions → /api/v1/admin/* (requires is_admin: true)
├── Headers → X-Session-Token (memory-only storage)
└── Error Handling → {data: {}, meta: {}, errors: []} format
```

### **Key Benefits of Auth Spec Alignment:**

#### **✅ Full API Compatibility**
- Complete alignment with `docs/02b_Authentication_Specifications.md`
- Proper authentication flow per security requirements
- Correct request/response format handling
- Unified login endpoint for all user types

#### **✅ Enhanced Security Compliance**
- Memory-only token storage (no localStorage)
- Proper session validation and cleanup
- Standardized error codes and messages
- Brute force protection UI handling

#### **✅ Improved User Experience**
- Real-time progress indicators
- Auth-specific error messages
- Automatic session management
- Graceful handling of session expiration

#### **✅ Production Readiness**
- Security compliance with auth specifications
- Performance targets alignment
- Proper error handling and recovery
- Role-based access control implementation

## Conclusion

This updated implementation plan provides a **fully corrected and comprehensive roadmap** for deploying a Vue.js frontend as the **primary interface** at `memo.myisland.dev` that properly aligns with the **updated Authentication Specifications** (`docs/02b_Authentication_Specifications.md`) and current backend API requirements. The corrections ensure:

1. **Primary Domain Deployment** - Vue frontend deployed at root domain with phase completion tracking
2. **Complete Auth Spec Compliance** - Full alignment with current security requirements and unified API endpoints
3. **Unified Authentication Flow** - Single login endpoint (`/api/v1/auth/login`) for all users, legacy admin endpoint removed
4. **Enhanced Security Implementation** - Memory-only token storage and standardized error handling
5. **Phase Tracking Homepage** - Real-time progress display of implementation status
6. **Production-Ready Architecture** - Security, performance, and maintainability optimizations

The Vue frontend will provide a modern, responsive interface that maintains complete compatibility with the existing backend while offering enhanced user experience, phase tracking, and full compliance with the updated authentication specifications.

**Next Steps**:
1. ✅ **Auth Spec Alignment Completed** - All corrections applied per `docs/02b_Authentication_Specifications.md`
2. **Begin Phase 1 Implementation** - Start with corrected project setup and unified authentication
3. **Follow Updated Plan** - Use corrected specifications throughout development
4. **Test Against Auth Specs** - Validate all authentication flows and security requirements

---

## 🎯 **CRITICAL REMINDERS FOR IMPLEMENTATION**

### **📋 Documentation Discipline**
- **EVERY STEP** must include both automated tests AND human browser testing
- **ALL CHANGES** must be documented in `vue_implementation_changelog.md`
- **LATEST CHANGES AT TOP** - Maintain reverse chronological order
- **VPS-FRIENDLY TESTS** - Ensure all human tests work on `https://memo.myisland.dev/` (primary domain)
- **PHASE TRACKING** - Update homepage phase status as implementation progresses

### **🔍 Human Testing Standards**
Each step must have browser-based testing covering:
- ✅ **Functional verification** - Does the feature work as expected?
- ✅ **Integration testing** - Does it work with the backend API?
- ✅ **Error handling** - How does it handle failures gracefully?
- ✅ **User experience** - Is the interface intuitive and responsive?
- ✅ **Security compliance** - Does it follow authentication specifications?

### **📝 Changelog Format Template**
```markdown
## [2024-MM-DD] Step X.Y Complete: Feature Name
- Implemented specific functionality with technical details
- Tested feature in browser at https://memo.myisland.dev/
- Verified integration with backend API endpoints
- Confirmed compliance with authentication specifications
- Status: ✅ Feature implemented and tested
```

### **🚨 Quality Gates**
**DO NOT PROCEED** to next step until:
1. ✅ Code is committed to repository
2. ✅ Automated tests pass
3. ✅ Human testing completed in browser
4. ✅ Documentation updated in changelog
5. ✅ No console errors or network failures

---

**Document History**:
- **v1.0**: Initial implementation plan created
- **v1.1**: Major corrections applied based on backend API review
- **v1.2**: Updated to align with `docs/02b_Authentication_Specifications.md`
- **v1.3**: Updated to reflect legacy admin endpoint removal and unified authentication system
- **v1.4**: Added comprehensive human testing requirements and documentation standards
- **v1.5**: Updated for primary domain deployment at `memo.myisland.dev/` with phase tracking homepage
- **Status**: Ready for primary domain implementation with phase tracking
- **Next Review**: After Phase 3 completion (authentication and API integration)
