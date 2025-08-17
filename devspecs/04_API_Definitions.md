# 04_API_Definitions.md

## 1.0 How to Use This File

1.1 **Audience**
- AI coding agents and human developers.

1.2 **Purpose**
- Defines the REST API endpoints, request/response formats, and API behavior for the Memo AI Coach project.
- Builds directly on the data model defined in `03_Data_Model.md`.

1.3 **Next Steps**
- Review this file before proceeding to `05_UI_UX.md`.

---

## 2.0 API Technology Stack

2.1 **Framework Decision**
- **Decision**: FastAPI (as specified in Architecture)
- **Rationale**: Lightweight, async-friendly, automatic OpenAPI documentation

2.2 **API Style**
- **Decision**: REST API
- **Rationale**: Simple, maintainable, follows standard conventions

2.3 **Authentication Strategy**
- **Decision**: (Pending)
- **Questions**:
  - Should we implement authentication for MVP?
  - How do we handle session management?
  - What level of security is required?

---

## 3.0 Base API Structure

3.1 **Base URL**
- **Development**: `http://localhost:8000`
- **Production**: (Pending) Define production URL structure

3.2 **API Versioning**
- **Decision**: (Pending)
- **Options**: URL versioning (`/api/v1/`), header versioning, no versioning for MVP
- **Questions**: Should we implement versioning from the start?

3.3 **Response Format**
```json
{
  "success": boolean,
  "data": object | array | null,
  "error": {
    "code": string,
    "message": string,
    "details": object
  } | null,
  "timestamp": string
}
```

---

## 4.0 Core API Endpoints

### 4.1 Evaluation Endpoints

#### 4.1.1 Submit Text for Evaluation
**Questions to Answer**:
- How do we handle large text submissions?
- What validation rules should apply?
- How do we handle concurrent submissions?

**Proposed Endpoint**:
```
POST /api/evaluations/submit
Content-Type: application/json

Request:
{
  "text": string,
  "session_id": string (optional),
  "metadata": object (optional)
}

Response:
{
  "success": true,
  "data": {
    "evaluation_id": string,
    "overall_score": number,
    "strengths": string,
    "opportunities": string,
    "rubric_scores": object,
    "segment_feedback": array,
    "processing_time": number
  }
}
```

#### 4.1.2 Get Evaluation Details
**Questions to Answer**:
- Should we include raw LLM responses in debug mode?
- How do we handle evaluation not found scenarios?

**Proposed Endpoint**:
```
GET /api/evaluations/{evaluation_id}
Query Parameters:
- include_debug: boolean (default: false)

Response:
{
  "success": true,
  "data": {
    "evaluation": object,
    "debug_info": object (if include_debug=true)
  }
}
```

### 4.2 Chat Endpoints

#### 4.2.1 Start Chat Session
**Questions to Answer**:
- How do we manage chat session lifecycle?
- Should we limit chat sessions per evaluation?

**Proposed Endpoint**:
```
POST /api/chat/sessions
Content-Type: application/json

Request:
{
  "evaluation_id": string
}

Response:
{
  "success": true,
  "data": {
    "session_id": string,
    "evaluation_context": object
  }
}
```

#### 4.2.2 Send Chat Message
**Questions to Answer**:
- How do we handle message length limits?
- Should we implement rate limiting?
- How do we maintain conversation context?

**Proposed Endpoint**:
```
POST /api/chat/sessions/{session_id}/messages
Content-Type: application/json

Request:
{
  "message": string
}

Response:
{
  "success": true,
  "data": {
    "message_id": string,
    "response": string,
    "timestamp": string
  }
}
```

### 4.3 Progress Tracking Endpoints

#### 4.3.1 Get Progress History
**Questions to Answer**:
- How do we aggregate progress data?
- What time periods should we support?
- How do we handle data privacy?

**Proposed Endpoint**:
```
GET /api/progress/history
Query Parameters:
- session_id: string
- time_period: string (day, week, month, all)
- metric_type: string (optional)

Response:
{
  "success": true,
  "data": {
    "metrics": array,
    "chart_data": object,
    "trends": object
  }
}
```

### 4.4 Admin Endpoints

#### 4.4.1 Get Configuration Files
**Questions to Answer**:
- How do we handle configuration validation?
- Should we support configuration versioning?
- How do we implement admin authentication?

**Proposed Endpoint**:
```
GET /api/admin/configurations/{config_type}
Response:
{
  "success": true,
  "data": {
    "config_type": string,
    "content": string,
    "version": number,
    "last_updated": string
  }
}
```

#### 4.4.2 Update Configuration Files
**Questions to Answer**:
- How do we validate YAML syntax?
- Should we implement rollback functionality?
- How do we handle configuration conflicts?

**Proposed Endpoint**:
```
PUT /api/admin/configurations/{config_type}
Content-Type: application/json

Request:
{
  "content": string,
  "version": number
}

Response:
{
  "success": true,
  "data": {
    "config_type": string,
    "new_version": number,
    "validation_result": object
  }
}
```

### 4.5 Debug Endpoints

#### 4.5.1 Get Debug Information
**Questions to Answer**:
- What debug information should be exposed?
- How do we handle sensitive data in debug mode?
- Should debug mode be configurable per request?

**Proposed Endpoint**:
```
GET /api/debug/info
Query Parameters:
- evaluation_id: string (optional)
- include_raw_data: boolean (default: false)

Response:
{
  "success": true,
  "data": {
    "performance_metrics": object,
    "system_status": object,
    "raw_prompts": array (if include_raw_data=true),
    "raw_responses": array (if include_raw_data=true)
  }
}
```

### 4.6 Export Endpoints

#### 4.6.1 Generate PDF Export
**Questions to Answer**:
- How do we handle PDF generation for large evaluations?
- Should we support different PDF formats/templates?
- How do we handle generation failures?

**Proposed Endpoint**:
```
POST /api/export/pdf
Content-Type: application/json

Request:
{
  "evaluation_id": string,
  "include_segments": boolean (default: true),
  "template": string (default: "standard")
}

Response:
{
  "success": true,
  "data": {
    "pdf_url": string,
    "file_size": number,
    "generation_time": number
  }
}
```

---

## 5.0 Error Handling

5.1 **HTTP Status Codes**
- **200**: Success
- **400**: Bad Request (validation errors)
- **404**: Not Found
- **422**: Unprocessable Entity (FastAPI validation)
- **500**: Internal Server Error

5.2 **Error Response Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid text content",
    "details": {
      "field": "text",
      "issue": "Text cannot be empty"
    }
  }
}
```

5.3 **Common Error Codes**
- **Questions to Answer**:
  - What specific error codes should we define?
  - How detailed should error messages be?
  - Should we implement error logging?

---

## 6.0 Rate Limiting and Security

6.1 **Rate Limiting**
- **Decision**: (Pending)
- **Questions**:
  - Should we implement rate limiting for MVP?
  - What limits should apply to different endpoints?
  - How do we handle rate limit violations?

6.2 **CORS Configuration**
- **Decision**: (Pending)
- **Questions**:
  - What origins should be allowed?
  - Should we implement CORS for development only?

6.3 **Input Validation**
- **Decision**: (Pending)
- **Questions**:
  - What validation rules should apply to text submissions?
  - How do we handle malicious input?
  - Should we implement content filtering?

---

## 7.0 API Documentation

7.1 **OpenAPI/Swagger**
- **Decision**: Use FastAPI's automatic OpenAPI generation
- **URL**: `/docs` for Swagger UI, `/redoc` for ReDoc

7.2 **API Examples**
- **Decision**: (Pending)
- **Questions**:
  - Should we provide example requests/responses?
  - How comprehensive should documentation be?

---

## 8.0 Testing Strategy

8.1 **API Testing**
- **Decision**: (Pending)
- **Questions**:
  - Should we use pytest for API testing?
  - How do we test LLM integration?
  - Should we implement integration tests?

---

## 9.0 Performance Considerations

9.1 **Response Times**
- **Target**: < 15 seconds for evaluation submissions (per Requirements)
- **Questions**:
  - How do we handle timeouts?
  - Should we implement async processing for long operations?

9.2 **Caching Strategy**
- **Decision**: (Pending)
- **Questions**:
  - Should we cache configuration files?
  - How do we handle cache invalidation?

---

## 10.0 Traceability Links

- **Source of Truth**: `03_Data_Model.md`
- **Mapped Requirements**: 
  - Text Evaluation (2.2)
  - Chat with LLM (2.3)
  - Progress Tracking (2.6)
  - Admin Functions (2.4)
  - Debug Mode (2.5)
  - PDF Export (2.7)

---

## 11.0 Open Questions and Decisions

11.1 **Critical Decisions Needed**:
- Authentication and session management strategy
- Rate limiting implementation
- Error handling and logging approach
- API versioning strategy
- Security implementation details

11.2 **Technical Decisions**:
- Input validation rules and implementation
- Caching strategy
- Performance optimization approach
- Testing framework and methodology
