# Admin LLM Debug Viewer Implementation Plan (Simplified)
## Memo AI Coach

**Document ID**: admin_llm_debug_viewer_implementation_plan.md
**Document Version**: 2.0
**Last Updated**: Phase 9
**Status**: Implementation Plan (Simplified Approach)

---

## 1.0 Overview

### 1.1 Purpose
Add an admin component to view raw LLM requests and responses for debugging and monitoring purposes. This simplified implementation leverages existing database infrastructure to provide administrators with visibility into the actual prompts sent to Claude API and the raw responses received, enabling better understanding of the evaluation process and troubleshooting of LLM interactions.

### 1.2 Key Features
- **Raw Request/Response Viewer**: Display the actual prompts sent to LLM and raw responses received
- **Collapsible Sections**: Handle long text content with expandable/collapsible sections
- **Clipboard Integration**: Copy text to clipboard with tooltip feedback
- **Admin-Only Access**: Restricted to administrators only
- **Last Evaluations Display**: View recent evaluations with raw data
- **User/Session Information**: Show which user performed each evaluation
- **Simple Filtering**: Basic filtering by user and date

### 1.3 Integration Points
- **Backend**: Activate existing database storage and add simple admin endpoints
- **Frontend**: New admin component integrated into existing Admin page
- **Database**: Leverage existing `raw_prompt` and `raw_response` fields in evaluations table
- **Authentication**: Admin-only access control using existing auth system

---

## 2.0 Phase 1: Backend Implementation

### 2.1 Database Schema Analysis
The existing `evaluations` table already contains the necessary fields:
- `raw_prompt`: Stores the actual prompt sent to LLM
- `raw_response`: Stores the raw response from LLM
- `debug_enabled`: Boolean flag for debug mode
- `llm_provider`: Provider information (claude)
- `llm_model`: Model information (claude-3-haiku-20240307)

**Current State**: These fields exist but are not being populated during evaluation.

### 2.2 Implementation Strategy
This simplified approach focuses on:
1. **Activating existing storage**: Modify LLM service to capture and store raw data
2. **Adding database persistence**: Update evaluation submission to save to database
3. **Simple admin endpoints**: Create basic endpoints to retrieve last evaluations
4. **No new database features**: Use existing schema and relationships

### 2.3 New API Endpoints

#### 2.3.1 Last Evaluations Endpoint
**Path**: `GET /api/v1/admin/last-evaluations`
**Authentication**: Admin only
**Purpose**: Retrieve last evaluation for each user with raw LLM data

**Response Format**:
```json
{
  "data": {
    "evaluations": [
      {
        "id": 123,
        "submission_id": 456,
        "overall_score": 4.2,
        "processing_time": 3.1,
        "created_at": "2024-01-01T00:00:00Z",
        "llm_provider": "claude",
        "llm_model": "claude-3-haiku-20240307",
        "debug_enabled": true,
        "has_raw_data": true,
        "submission_preview": "First 100 characters of memo...",
        "username": "john_doe",
        "is_admin": false
      }
    ],
    "total": 5
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  },
  "errors": []
}
```

#### 2.3.2 Raw Data Endpoint
**Path**: `GET /api/v1/admin/evaluation/{evaluation_id}/raw`
**Authentication**: Admin only
**Purpose**: Retrieve raw LLM data for a specific evaluation

**Response Format**:
```json
{
  "data": {
    "evaluation": {
      "id": 123,
      "submission_id": 456,
      "overall_score": 4.2,
      "processing_time": 3.1,
      "created_at": "2024-01-01T00:00:00Z",
      "llm_provider": "claude",
      "llm_model": "claude-3-haiku-20240307",
      "debug_enabled": true,
      "raw_prompt": "System message and user prompt content...",
      "raw_response": "Raw LLM response content...",
      "submission": {
        "id": 456,
        "content": "Original memo text content...",
        "created_at": "2024-01-01T00:00:00Z"
      }
    }
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "uuid"
  },
  "errors": []
}
```

### 2.4 Backend Code Implementation

#### 2.4.1 Update LLM Service (15 minutes)
Modify `backend/services/llm_service.py` to capture raw prompts and responses:

```python
def evaluate_text(self, text_content: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    # ... existing code until API call ...
    
    # Generate prompt
    system_message, user_message = self._generate_prompt(text_content)
    raw_prompt = f"System: {system_message}\n\nUser: {user_message}"
    
    # Make API call
    response = self.client.messages.create(...)
    
    # Extract response content
    response_text = response.content[0].text if response.content else ""
    raw_response = response_text
    
    # Parse response
    evaluation_data = self._parse_response(response_text)
    
    # Add raw data to evaluation_data
    evaluation_data['raw_prompt'] = raw_prompt
    evaluation_data['raw_response'] = raw_response
    
    # ... rest of existing code ...
```

#### 2.4.2 Update Main API (30 minutes)
Modify `backend/main.py` to add database persistence:

```python
@app.post("/api/v1/evaluations/submit")
async def submit_evaluation(request: Request):
    # ... existing authentication and validation ...
    
    # Create submission record
    submission = Submission.create(text_content, session_data['session_id'])
    
    # Use LLM service for text evaluation
    success, evaluation_result, error = evaluate_text_with_llm(text_content)
    
    if success:
        # Create evaluation record with raw data
        evaluation = Evaluation.create(
            submission_id=submission.id,
            overall_score=evaluation_result['overall_score'],
            strengths=json.dumps(evaluation_result['strengths']),
            opportunities=json.dumps(evaluation_result['opportunities']),
            rubric_scores=json.dumps(evaluation_result['rubric_scores']),
            segment_feedback=json.dumps(evaluation_result['segment_feedback']),
            llm_provider='claude',
            llm_model=evaluation_result.get('model_used', 'claude-3-haiku-20240307'),
            raw_prompt=evaluation_result.get('raw_prompt'),
            raw_response=evaluation_result.get('raw_response'),
            debug_enabled=True,  # Enable debug mode
            processing_time=evaluation_result.get('processing_time')
        )
    
    # ... rest of existing code ...
```

#### 2.4.3 Add Admin Endpoints (45 minutes)
Add to `backend/main.py`:

```python
@app.get("/api/v1/admin/last-evaluations")
async def get_last_evaluations(request: Request):
    """Get last evaluation for each user (admin only)"""
    # ... authentication and admin check ...
    
    try:
        # Get last evaluation for each user
        query = """
            SELECT 
                e.id, e.submission_id, e.overall_score, e.processing_time,
                e.created_at, e.llm_provider, e.llm_model, e.debug_enabled,
                e.raw_prompt, e.raw_response,
                s.text_content as submission_content,
                u.username, u.is_admin
            FROM evaluations e
            JOIN submissions s ON e.submission_id = s.id
            JOIN sessions sess ON s.session_id = sess.session_id
            JOIN users u ON sess.user_id = u.id
            WHERE e.id IN (
                SELECT MAX(e2.id) FROM evaluations e2
                JOIN submissions s2 ON e2.submission_id = s2.id
                JOIN sessions sess2 ON s2.session_id = sess2.session_id
                GROUP BY sess2.user_id
            )
            ORDER BY e.created_at DESC
            LIMIT 50
        """
        
        result = db_manager.execute_query(query)
        
        evaluations = []
        for row in result:
            evaluations.append({
                "id": row['id'],
                "submission_id": row['submission_id'],
                "overall_score": row['overall_score'],
                "processing_time": row['processing_time'],
                "created_at": row['created_at'],
                "llm_provider": row['llm_provider'],
                "llm_model": row['llm_model'],
                "debug_enabled": bool(row['debug_enabled']),
                "has_raw_data": bool(row['raw_prompt'] and row['raw_response']),
                "submission_preview": row['submission_content'][:100] + "..." if len(row['submission_content']) > 100 else row['submission_content'],
                "username": row['username'],
                "is_admin": bool(row['is_admin'])
            })
        
        return {
            "data": {
                "evaluations": evaluations,
                "total": len(evaluations)
            },
            "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": str(uuid.uuid4())},
            "errors": []
        }
    except Exception as e:
        logger.error(f"Failed to get last evaluations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/admin/evaluation/{evaluation_id}/raw")
async def get_evaluation_raw_data(evaluation_id: int, request: Request):
    """Get raw data for specific evaluation (admin only)"""
    # ... authentication and admin check ...
    
    try:
        evaluation = Evaluation.get_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")
        
        submission = Submission.get_by_id(evaluation.submission_id)
        
        return {
            "data": {
                "evaluation": {
                    "id": evaluation.id,
                    "submission_id": evaluation.submission_id,
                    "overall_score": evaluation.overall_score,
                    "processing_time": evaluation.processing_time,
                    "created_at": evaluation.created_at.isoformat(),
                    "llm_provider": evaluation.llm_provider,
                    "llm_model": evaluation.llm_model,
                    "debug_enabled": evaluation.debug_enabled,
                    "raw_prompt": evaluation.raw_prompt,
                    "raw_response": evaluation.raw_response,
                    "submission": {
                        "id": submission.id if submission else None,
                        "content": submission.text_content if submission else "",
                        "created_at": submission.created_at.isoformat() if submission else None
                    }
                }
            },
            "meta": {"timestamp": datetime.utcnow().isoformat(), "request_id": str(uuid.uuid4())},
            "errors": []
        }
    except Exception as e:
        logger.error(f"Failed to get evaluation raw data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2.5 Phase 1 Testing

#### 2.5.1 Automated Tests
Create `tests/test_last_evaluations_api.py`:

```python
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestLastEvaluationsAPI:
    def test_get_last_evaluations_unauthorized(self):
        response = client.get("/api/v1/admin/last-evaluations")
        assert response.status_code == 401
    
    def test_get_last_evaluations_non_admin(self, regular_user_session):
        headers = {"X-Session-Token": regular_user_session}
        response = client.get("/api/v1/admin/last-evaluations", headers=headers)
        assert response.status_code == 403
    
    def test_get_last_evaluations_admin_success(self, admin_session):
        headers = {"X-Session-Token": admin_session}
        response = client.get("/api/v1/admin/last-evaluations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data and "evaluations" in data["data"]
    
    def test_get_evaluation_raw_data_unauthorized(self):
        response = client.get("/api/v1/admin/evaluation/1/raw")
        assert response.status_code == 401
    
    def test_get_evaluation_raw_data_not_found(self, admin_session):
        headers = {"X-Session-Token": admin_session}
        response = client.get("/api/v1/admin/evaluation/99999/raw", headers=headers)
        assert response.status_code == 404
```

#### 2.5.2 Human Testing Checklist
**Backend API Testing** (5 minutes):
- [ ] Login as admin user
- [ ] Test `/api/v1/admin/last-evaluations` endpoint returns 200
- [ ] Test `/api/v1/admin/evaluation/{id}/raw` endpoint returns 200
- [ ] Verify non-admin users get 403 error
- [ ] Verify unauthorized requests get 401 error

---

## 3.0 Phase 2: Frontend Implementation

### 3.1 New Admin Component

#### 3.1.1 Component Structure
Create `vue-frontend/src/components/admin/LastEvaluationsViewer.vue`:

```vue
<template>
  <div class="bg-white rounded-lg shadow-lg p-6">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-semibold text-gray-900">
        🔍 Last Evaluations Raw Data
      </h3>
      <button
        @click="refreshData"
        :disabled="loading"
        class="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Evaluations List -->
    <div class="space-y-4">
      <div
        v-for="evaluation in evaluations"
        :key="evaluation.id"
        class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
      >
        <div class="flex justify-between items-start mb-3">
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-medium text-gray-900">
                {{ evaluation.username }}
              </span>
              <span v-if="evaluation.is_admin" class="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                Admin
              </span>
              <span class="text-sm text-gray-500">
                {{ formatDate(evaluation.created_at) }}
              </span>
            </div>
            <div class="text-sm text-gray-600 mt-1">
              Score: {{ evaluation.overall_score }} | 
              Time: {{ evaluation.processing_time }}s | 
              Model: {{ evaluation.llm_model }}
            </div>
          </div>
          <button
            v-if="evaluation.has_raw_data"
            @click="viewRawData(evaluation)"
            class="px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600"
          >
            View Raw Data
          </button>
          <span v-else class="text-sm text-gray-400">No Raw Data</span>
        </div>
        <div class="text-sm text-gray-500">
          {{ evaluation.submission_preview }}
        </div>
      </div>
    </div>

    <!-- Raw Data Modal -->
    <div
      v-if="showRawDataModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeRawDataModal"
    >
      <div
        class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
        @click.stop
      >
        <div class="flex justify-between items-center mb-4">
          <h4 class="text-xl font-semibold text-gray-900">
            Raw LLM Data - Evaluation #{{ selectedEvaluation?.id }}
          </h4>
          <button @click="closeRawDataModal" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div v-if="rawDataLoading" class="text-center py-8">
          <div class="text-gray-500">Loading raw data...</div>
        </div>

        <div v-else-if="rawData" class="space-y-6">
          <!-- Submission Content -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Original Submission</h5>
              <button
                @click="copyToClipboard(rawData.submission.content)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.submission.content"
              :max-height="200"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>

          <!-- Raw Prompt -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Raw Prompt Sent to LLM</h5>
              <button
                @click="copyToClipboard(rawData.evaluation.raw_prompt)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.evaluation.raw_prompt"
              :max-height="300"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>

          <!-- Raw Response -->
          <div class="border border-gray-200 rounded-lg p-4">
            <div class="flex justify-between items-center mb-2">
              <h5 class="font-semibold text-gray-900">Raw Response from LLM</h5>
              <button
                @click="copyToClipboard(rawData.evaluation.raw_response)"
                class="text-blue-500 hover:text-blue-700 text-sm"
                title="Copy to clipboard"
              >
                📋 Copy
              </button>
            </div>
            <CollapsibleText
              :text="rawData.evaluation.raw_response"
              :max-height="300"
              class="bg-gray-50 p-3 rounded text-sm font-mono"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Copy Success Toast -->
    <div
      v-if="showCopyToast"
      class="fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50"
    >
      Copied to clipboard!
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { apiClient } from '@/services/api'
import CollapsibleText from '@/components/CollapsibleText.vue'

// Types
interface Evaluation {
  id: number
  submission_id: number
  overall_score: number
  processing_time: number
  created_at: string
  llm_provider: string
  llm_model: string
  debug_enabled: boolean
  has_raw_data: boolean
  submission_preview: string
  username: string
  is_admin: boolean
}

interface RawData {
  evaluation: {
    id: number
    submission_id: number
    overall_score: number
    processing_time: number
    created_at: string
    llm_provider: string
    llm_model: string
    debug_enabled: boolean
    raw_prompt: string
    raw_response: string
  }
  submission: {
    id: number
    content: string
    created_at: string
  }
}

// Reactive data
const evaluations = ref<Evaluation[]>([])
const loading = ref(false)
const rawDataLoading = ref(false)
const showRawDataModal = ref(false)
const selectedEvaluation = ref<Evaluation | null>(null)
const rawData = ref<RawData | null>(null)
const showCopyToast = ref(false)

// Methods
const loadEvaluations = async () => {
  try {
    loading.value = true
    const result = await apiClient.get('/api/v1/admin/last-evaluations')
    
    if (result.success) {
      evaluations.value = result.data.evaluations
    }
  } catch (error) {
    console.error('Failed to load evaluations:', error)
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadEvaluations()
}

const viewRawData = async (evaluation: Evaluation) => {
  try {
    rawDataLoading.value = true
    showRawDataModal.value = true
    selectedEvaluation.value = evaluation
    
    const result = await apiClient.get(`/api/v1/admin/evaluation/${evaluation.id}/raw`)
    
    if (result.success) {
      rawData.value = result.data.evaluation
    }
  } catch (error) {
    console.error('Failed to load raw data:', error)
  } finally {
    rawDataLoading.value = false
  }
}

const closeRawDataModal = () => {
  showRawDataModal.value = false
  selectedEvaluation.value = null
  rawData.value = null
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    showCopyToast.value = true
    setTimeout(() => {
      showCopyToast.value = false
    }, 2000)
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
  }
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// Lifecycle
onMounted(() => {
  loadEvaluations()
})
</script>
```

#### 3.1.2 Collapsible Text Component
Create `vue-frontend/src/components/CollapsibleText.vue`:

```vue
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
```

### 3.2 Update Admin Page
Update `vue-frontend/src/views/Admin.vue` to include the new component:

```vue
<template>
  <Layout>
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 mb-6">
          Admin Panel
        </h1>
        
        <div class="grid md:grid-cols-2 gap-6 mb-6">
          <!-- Health Monitoring -->
          <div class="bg-blue-50 rounded-lg p-6 border-l-4 border-blue-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🏥 Health Monitoring
            </h3>
            <HealthStatus />
          </div>
          
          <!-- Configuration Validation -->
          <div class="bg-green-50 rounded-lg p-6 border-l-4 border-green-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              ✅ Configuration Validation
            </h3>
            <ConfigValidator />
          </div>
          
          <!-- User Management -->
          <div class="bg-yellow-50 rounded-lg p-6 border-l-4 border-yellow-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              👥 User Management
            </h3>
            <UserManagement />
          </div>
          
          <!-- Session Management -->
          <div class="bg-purple-50 rounded-lg p-6 border-l-4 border-purple-500">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              🔗 Session Management
            </h3>
            <SessionManagement />
          </div>
        </div>

        <!-- Last Evaluations Viewer - Full Width -->
        <div class="bg-orange-50 rounded-lg p-6 border-l-4 border-orange-500">
          <LastEvaluationsViewer />
        </div>
      </div>
    </div>
  </Layout>
</template>

<script setup lang="ts">
import Layout from '@/components/Layout.vue'
import HealthStatus from '@/components/admin/HealthStatus.vue'
import ConfigValidator from '@/components/admin/ConfigValidator.vue'
import UserManagement from '@/components/admin/UserManagement.vue'
import SessionManagement from '@/components/admin/SessionManagement.vue'
import LastEvaluationsViewer from '@/components/admin/LastEvaluationsViewer.vue'
</script>
```

### 3.3 API Service Integration
Update `vue-frontend/src/services/api.ts` to include the new endpoints:

```typescript
// Add to existing API service
export const lastEvaluationsApi = {
  // Get last evaluations for all users
  getLastEvaluations: async () => {
    return await apiClient.get('/api/v1/admin/last-evaluations')
  },

  // Get raw LLM data for specific evaluation
  getRawData: async (evaluationId: number) => {
    return await apiClient.get(`/api/v1/admin/evaluation/${evaluationId}/raw`)
  }
}

// Export the apiClient instance for direct use
export { apiClient }
```

### 3.4 Phase 2 Testing

#### 3.4.1 Automated Tests
Create `vue-frontend/tests/components/CollapsibleText.test.js`:

```javascript
import { mount } from '@vue/test-utils'
import CollapsibleText from '@/components/CollapsibleText.vue'

describe('CollapsibleText', () => {
  it('renders text content correctly', () => {
    const wrapper = mount(CollapsibleText, {
      props: { text: 'Test content' }
    })
    expect(wrapper.text()).toContain('Test content')
  })

  it('shows expand button for long content', async () => {
    const longText = 'A'.repeat(200)
    const wrapper = mount(CollapsibleText, {
      props: { text: longText, maxHeight: 100 }
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('toggles expanded state when button is clicked', async () => {
    const longText = 'A'.repeat(200)
    const wrapper = mount(CollapsibleText, {
      props: { text: longText, maxHeight: 100 }
    })
    await wrapper.vm.$nextTick()
    const button = wrapper.find('button')
    await button.trigger('click')
    expect(button.text()).toContain('Show Less')
  })
})
```

Create `vue-frontend/tests/components/LastEvaluationsViewer.test.js`:

```javascript
import { mount } from '@vue/test-utils'
import LastEvaluationsViewer from '@/components/admin/LastEvaluationsViewer.vue'

jest.mock('@/services/api', () => ({
  apiClient: { get: jest.fn() }
}))

describe('LastEvaluationsViewer', () => {
  it('renders component title correctly', () => {
    const wrapper = mount(LastEvaluationsViewer)
    expect(wrapper.find('h3').text()).toContain('Last Evaluations Raw Data')
  })

  it('loads evaluations on mount', async () => {
    const { apiClient } = require('@/services/api')
    apiClient.get.mockResolvedValue({
      success: true,
      data: { evaluations: [] }
    })
    const wrapper = mount(LastEvaluationsViewer)
    await wrapper.vm.$nextTick()
    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/admin/last-evaluations')
  })
})
```

#### 3.4.2 Human Testing Checklist
**Frontend Component Testing** (10 minutes):
- [ ] Navigate to `/admin` page
- [ ] Verify "Last Evaluations Raw Data" section appears
- [ ] Click "Refresh" button - should load evaluations
- [ ] Click "View Raw Data" for an evaluation
- [ ] Verify modal opens with submission, prompt, and response
- [ ] Test "Show More/Less" buttons for long text
- [ ] Click copy buttons - should show "Copied to clipboard!" toast
- [ ] Close modal and verify it disappears

---

## 4.0 Phase 3: Integration Testing

### 4.1 End-to-End Testing

#### 4.1.1 Automated E2E Tests
Create `tests/e2e/test_last_evaluations_flow.py`:

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestLastEvaluationsE2E:
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_admin_login_and_navigation(self, driver):
        driver.get("http://localhost:3000/login")
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("admin123")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Admin')]"))
        )
        admin_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Admin')]")
        admin_link.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Admin Panel')]"))
        )
        assert "Admin Panel" in driver.page_source
    
    def test_last_evaluations_section(self, driver):
        self.test_admin_login_and_navigation(driver)
        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Last Evaluations Raw Data')]"))
        )
        assert "Last Evaluations Raw Data" in section.text
    
    def test_view_raw_data_modal(self, driver):
        self.test_admin_login_and_navigation(driver)
        view_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'View Raw Data')]"))
        )
        view_button.click()
        modal = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'modal')]"))
        )
        assert "Raw LLM Data" in modal.text
```

#### 4.1.2 Performance Tests
Create `tests/performance/test_last_evaluations_performance.py`:

```python
import time
import requests
import statistics

BASE_URL = "http://localhost:8000"

def test_api_response_times():
    print("🚀 Testing API Response Times...")
    
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    session_token = response.json()["data"]["session_token"]
    headers = {"X-Session-Token": session_token}
    
    times = []
    for i in range(10):
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/v1/admin/last-evaluations", headers=headers)
        end_time = time.time()
        times.append(end_time - start_time)
    
    avg_time = statistics.mean(times)
    max_time = max(times)
    
    print(f"📊 Last Evaluations API Performance:")
    print(f"   Average: {avg_time:.3f}s")
    print(f"   Maximum: {max_time:.3f}s")
    
    assert avg_time < 1.0, f"Average response time {avg_time:.3f}s exceeds 1.0s limit"
    assert max_time < 2.0, f"Maximum response time {max_time:.3f}s exceeds 2.0s limit"
    
    print("✅ API performance tests passed")

if __name__ == "__main__":
    test_api_response_times()
    print("\n🎉 All performance tests completed")
```

#### 4.1.3 Human Testing Checklist
**Integration Testing** (15 minutes):
- [ ] Submit a new memo evaluation as regular user
- [ ] Login as admin and go to `/admin`
- [ ] Verify new evaluation appears in Last Evaluations list
- [ ] Click "View Raw Data" and verify all content loads
- [ ] Test copy functionality for all three sections
- [ ] Verify responsive design on mobile/tablet
- [ ] Test with very long memo content (>1000 words)
- [ ] Verify error handling when backend is down

---

## 5.0 Phase 4: Deployment

### 5.1 Production Deployment Tests
Create `tests/deployment/test_production_deployment.py`:

```python
import requests
import subprocess
import time

PRODUCTION_URL = "https://your-domain.com"

def test_production_health():
    print("🏥 Testing Production Health...")
    response = requests.get(f"{PRODUCTION_URL}/health", timeout=10)
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    data = response.json()
    assert data["data"]["status"] == "healthy", "System not healthy"
    print("✅ Production health check passed")

def test_production_api_endpoints():
    print("🔌 Testing Production API Endpoints...")
    response = requests.get(f"{PRODUCTION_URL}/api/v1/admin/last-evaluations")
    assert response.status_code == 401, "Endpoint should require authentication"
    response = requests.get(f"{PRODUCTION_URL}/api/v1/admin/evaluation/1/raw")
    assert response.status_code == 401, "Endpoint should require authentication"
    print("✅ Production API endpoints accessible")

def test_docker_deployment():
    print("🐳 Testing Docker Deployment...")
    result = subprocess.run(["docker", "compose", "build"], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker build failed: {result.stderr}"
    result = subprocess.run(["docker", "compose", "up", "-d"], capture_output=True, text=True)
    assert result.returncode == 0, f"Docker compose up failed: {result.stderr}"
    time.sleep(30)
    response = requests.get("http://localhost/health", timeout=10)
    assert response.status_code == 200, "Local deployment health check failed"
    subprocess.run(["docker", "compose", "down"], capture_output=True)
    print("✅ Docker deployment test passed")

if __name__ == "__main__":
    test_production_health()
    test_production_api_endpoints()
    test_docker_deployment()
    print("\n🎉 All deployment tests completed")
```

### 5.2 Human Testing Checklist
**Production Deployment** (10 minutes):
- [ ] Deploy to production environment
- [ ] Verify health endpoint returns healthy status
- [ ] Test admin login and access to Last Evaluations
- [ ] Submit test evaluation and verify raw data storage
- [ ] Verify all copy-to-clipboard functionality works
- [ ] Test responsive design on production
- [ ] Verify error handling and user feedback

---

## 6.0 Implementation Timeline

### 6.1 Phase Breakdown
- **Phase 1: Backend Implementation** (1.5 hours)
  - Update LLM Service (15 minutes)
  - Add Database Persistence (30 minutes)
  - Add Admin Endpoints (45 minutes)
  - Backend Testing (30 minutes)

- **Phase 2: Frontend Implementation** (2.5 hours)
  - Create CollapsibleText Component (1 hour)
  - Create LastEvaluationsViewer Component (1.5 hours)
  - Update Admin Page (30 minutes)
  - Frontend Testing (30 minutes)

- **Phase 3: Integration Testing** (1 hour)
  - End-to-End Testing (30 minutes)
  - Performance Testing (30 minutes)
  - Integration Testing (30 minutes)

- **Phase 4: Deployment** (30 minutes)
  - Production Deployment (15 minutes)
  - Final Testing (15 minutes)

**Total Implementation Time: 5.5 hours**

---

## 7.0 Technical Considerations

### 7.1 Performance
- **Simple Queries**: Use existing database indexes for basic queries
- **Lazy Loading**: Load raw data only when requested
- **Limited Data**: Only store last evaluation per user to minimize storage

### 7.2 Security
- **Admin-Only Access**: Use existing authentication system
- **Data Sanitization**: Sanitize raw data before display
- **Existing Rate Limiting**: Leverage existing Traefik rate limiting

### 7.3 User Experience
- **Loading States**: Clear loading indicators
- **Error Handling**: User-friendly error messages
- **Responsive Design**: Mobile-friendly interface
- **Simple Interface**: Focus on core functionality

### 7.4 Data Management
- **Minimal Storage**: Only store last evaluation per user
- **Existing Backup**: Leverage existing database backup system
- **Privacy**: Raw data only accessible to administrators

---

## 8.0 Success Criteria

### 8.1 Functional Requirements
- [ ] Admin can view list of last evaluations for all users
- [ ] Admin can view detailed raw prompt and response for any evaluation
- [ ] Long text content is properly handled with collapsible sections
- [ ] Copy to clipboard functionality works with tooltip feedback
- [ ] User information is displayed for each evaluation
- [ ] Admin-only access is properly enforced

### 8.2 Performance Requirements
- [ ] Page load time < 2 seconds
- [ ] Raw data modal opens < 1 second
- [ ] Clipboard operations complete < 500ms
- [ ] Handles evaluations with large text content (>10KB)

### 8.3 Quality Requirements
- [ ] All code follows project coding standards
- [ ] Comprehensive error handling implemented
- [ ] Responsive design works on all screen sizes
- [ ] Security requirements satisfied
- [ ] Minimal database impact

---

## 9.0 Future Enhancements

### 9.1 Evolution Path to Full Database
This simplified implementation serves as a foundation for a full historical database:

**Phase 1: Current Implementation**
- Last evaluation per user
- Basic raw data display
- Simple admin interface

**Phase 2: Enhanced Storage**
- Store all evaluations (not just last)
- Add pagination and filtering
- Enhanced search capabilities

**Phase 3: Full Historical Database**
- Complete evaluation history
- Advanced analytics
- Export functionality
- Performance monitoring

### 9.2 Advanced Features (Future)
- **Search and Filter**: Advanced search capabilities
- **Export Functionality**: Export raw data to various formats
- **Analytics**: LLM performance analytics and metrics
- **Real-time Monitoring**: Live monitoring of LLM interactions

### 9.3 Integration Opportunities
- **Logging Integration**: Integrate with system logging
- **Alerting**: Alert on LLM errors or performance issues
- **Dashboard**: Comprehensive admin dashboard
- **API Documentation**: Auto-generated API documentation

---

## 10.0 References
- `docs/05_API_Documentation.md` - API specifications and patterns
- `docs/07_Administration_Guide.md` - Admin interface guidelines
- `backend/services/llm_service.py` - LLM service implementation
- `backend/models/entities.py` - Database entity models
- `vue-frontend/src/views/Admin.vue` - Admin page structure
- `vue-frontend/src/components/admin/` - Admin component patterns

---

## 11.0 Summary

This simplified implementation plan provides a **minimal viable solution** for viewing raw LLM requests and responses with the following benefits:

### **Key Advantages:**
1. **Leverages Existing Infrastructure**: Uses existing database schema and authentication
2. **Minimal Development Time**: 5.5 hours total implementation
3. **Immediate Value**: Provides raw data visibility right away
4. **Natural Evolution**: Easy to expand to full historical database
5. **Risk Mitigation**: Tests the concept before full implementation

### **What This Delivers:**
- Last Evaluations section integrated into existing Admin page
- Raw prompt and response viewing for last evaluations
- Collapsible text sections for long content
- Copy-to-clipboard functionality
- Admin-only access control
- User information display
- Simple, clean interface

### **Evolution Path:**
This implementation serves as the foundation for a full historical database system, allowing for incremental development and user feedback before committing to a more complex solution.
