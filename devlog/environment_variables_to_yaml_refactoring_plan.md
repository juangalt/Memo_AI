# Implementation Plan: Environment Variables to YAML Configuration Refactoring

## 🎯 **Overview**

This plan refactors hardcoded environment variables in `docker-compose.yml` to use YAML configuration as the source of truth, learning from recent fixes to session timeout and timezone issues.

## 🎯 **Goals**

1. **Centralize Configuration**: Move all configurable values to YAML files
2. **Eliminate Duplicates**: Remove duplicate environment variables that have YAML equivalents
3. **Maintain Security**: Keep sensitive data (API keys, passwords) as environment variables
4. **Ensure Backward Compatibility**: Maintain existing functionality during transition
5. **Add Comprehensive Testing**: Test each phase thoroughly before proceeding

## 📚 **Lessons Learned from Recent Fixes**

1. **Configuration Precedence**: YAML should override environment variables, not vice versa
2. **Timezone Handling**: Ensure proper UTC date parsing in frontend components
3. **Session Management**: Session timeouts are immutable once created
4. **Debug Logging**: Add temporary logging to verify configuration loading
5. **Incremental Testing**: Test each change before proceeding to next phase

---

## 🚀 **Phase 1: Remove Duplicate LLM Configuration**

### **Objective**: Remove environment variables that duplicate YAML settings

### **Changes Required**:

#### **1.1 Remove from docker-compose.yml**
```yaml
# Remove these lines from backend service:
- LLM_TIMEOUT=${LLM_TIMEOUT:-30}
- LLM_PROVIDER=${LLM_PROVIDER:-claude}
- LLM_MODEL=${LLM_MODEL:-claude-3-sonnet-20240229}
```

#### **1.2 Verify YAML Configuration**
- ✅ `config/llm.yaml` already has:
  - `api_configuration.timeout: 30`
  - `provider.name: "claude"`
  - `provider.model: "claude-3-haiku-20240307"`

#### **1.3 Update Backend ConfigService**
- Ensure `ConfigService` reads LLM settings from YAML
- Add debug logging to confirm YAML values are loaded

#### **1.4 Testing Steps**:
1. **Pre-test**: Verify current LLM functionality
2. **Remove variables**: Update docker-compose.yml
3. **Rebuild**: `docker compose build backend && docker compose up -d backend`
4. **Test LLM**: Submit evaluation request
5. **Verify logs**: Check backend logs for YAML configuration loading
6. **Health check**: Verify `/health` endpoint shows correct LLM settings

---

## 🚀 **Phase 2: Remove Duplicate Rate Limiting Configuration**

### **Objective**: Remove environment variables that duplicate auth YAML settings

### **Changes Required**:

#### **2.1 Remove from docker-compose.yml**
```yaml
# Remove these lines from backend service:
- RATE_LIMIT_PER_SESSION=${RATE_LIMIT_PER_SESSION:-20}
- RATE_LIMIT_PER_HOUR=${RATE_LIMIT_PER_HOUR:-1000}
```

#### **2.2 Verify YAML Configuration**
- ✅ `config/auth.yaml` already has:
  - `rate_limiting.requests_per_session_per_hour: 20`
  - `rate_limiting.global_requests_per_hour: 1000`

#### **2.3 Update Backend AuthService**
- Ensure `AuthService` reads rate limiting from YAML
- Add debug logging to confirm rate limiting settings

#### **2.4 Testing Steps**:
1. **Pre-test**: Verify current rate limiting functionality
2. **Remove variables**: Update docker-compose.yml
3. **Rebuild**: `docker compose build backend && docker compose up -d backend`
4. **Test rate limiting**: Make multiple rapid requests
5. **Verify logs**: Check backend logs for rate limiting configuration
6. **Health check**: Verify `/health` endpoint shows correct auth settings

---

## 🚀 **Phase 3: Add Missing Configuration to YAML**

### **Objective**: Add configuration values that should be in YAML but aren't

### **Changes Required**:

#### **3.1 Add to config/auth.yaml**
```yaml
session_management:
  # Add these new fields:
  max_concurrent_users: 100
  log_level: "INFO"
  session_warning_threshold: 10  # minutes
  session_refresh_interval: 60   # seconds
```

#### **3.2 Create config/deployment.yaml**
```yaml
# New file for deployment-specific settings
traefik:
  admin_email: "admin@example.com"
  domain: "memo.myisland.dev"
  rate_limit_average: 100
  rate_limit_burst: 200

database:
  url: "sqlite:///data/memoai.db"
  type: "sqlite"
  max_connections: 10

frontend:
  backend_url: "https://memo.myisland.dev"
  phase_tracking_enabled: true
  debug_console_log_limit: 50
```

#### **3.3 Update Backend ConfigService**
- Add support for new YAML files
- Add debug logging for new configuration loading

#### **3.4 Testing Steps**:
1. **Create YAML files**: Add new configuration files
2. **Update ConfigService**: Add support for new configs
3. **Rebuild**: `docker compose build backend && docker compose up -d backend`
4. **Test configuration**: Verify new settings are loaded
5. **Verify logs**: Check for new configuration loading messages
6. **Health check**: Verify `/health` endpoint shows new settings

---

## 🚀 **Phase 4: Remove Remaining Hardcoded Environment Variables**

### **Objective**: Remove environment variables that now have YAML equivalents

### **Changes Required**:

#### **4.1 Remove from docker-compose.yml**
```yaml
# Remove from backend service:
- LOG_LEVEL=${LOG_LEVEL:-INFO}
- MAX_CONCURRENT_USERS=${MAX_CONCURRENT_USERS:-100}

# Remove from traefik service:
- "--certificatesresolvers.letsencrypt.acme.email=${ADMIN_EMAIL:-admin@example.com}"

# Remove from vue-frontend service:
- VITE_BACKEND_URL=https://memo.myisland.dev
```

#### **4.2 Update docker-compose.yml to use YAML values**
```yaml
# Update traefik command to read from YAML
command:
  - "--certificatesresolvers.letsencrypt.acme.email=${TRAEFIK_ADMIN_EMAIL}"
```

#### **4.3 Update Backend to Read from YAML**
- Ensure all removed environment variables are read from YAML
- Add comprehensive error handling for missing YAML values

#### **4.4 Testing Steps**:
1. **Pre-test**: Verify all functionality works with current setup
2. **Remove variables**: Update docker-compose.yml
3. **Rebuild**: `docker compose build backend vue-frontend && docker compose up -d`
4. **Test functionality**: Verify all features still work
5. **Verify logs**: Check for YAML configuration loading
6. **Health check**: Verify `/health` endpoint shows correct settings

---

## 🚀 **Phase 5: Frontend Configuration Integration**

### **Objective**: Update frontend to read configuration from backend

### **Changes Required**:

#### **5.1 Create Frontend Config Endpoint**
```python
# Add to backend/main.py
@app.get("/api/v1/config/frontend")
async def get_frontend_config():
    """Get frontend-specific configuration"""
    return {
        "data": {
            "session_warning_threshold": 10,
            "session_refresh_interval": 60,
            "debug_console_log_limit": 50,
            "llm_timeout_expectation": 15,
            "default_response_time": 1000
        }
    }
```

#### **5.2 Update Frontend Components**
- Update `SessionManagement.vue` to use configurable values
- Update `DevelopmentTools.vue` to use configurable log limit
- Update `ApiHealthTesting.vue` to use configurable timeout expectations

#### **5.3 Create Frontend Config Service**
```typescript
// Create vue-frontend/src/services/config.ts
export const configService = {
  async getFrontendConfig() {
    return apiClient.get('/api/v1/config/frontend')
  }
}
```

#### **5.4 Testing Steps**:
1. **Add backend endpoint**: Create frontend config endpoint
2. **Update frontend**: Modify components to use config service
3. **Rebuild**: `docker compose build vue-frontend && docker compose up -d vue-frontend`
4. **Test admin panel**: Verify session management shows correct values
5. **Test debug page**: Verify debug tools use configurable limits
6. **Test API testing**: Verify timeout expectations are configurable

---

## 🚀 **Phase 6: Validation and Cleanup**

### **Objective**: Final validation and cleanup

### **Changes Required**:

#### **6.1 Comprehensive Testing**
- Test all admin functions
- Test all debug functions
- Test authentication and session management
- Test LLM evaluation functionality
- Test rate limiting
- Test health endpoints

#### **6.2 Remove Debug Logging**
- Remove temporary debug logging added during development
- Keep essential logging for configuration loading

#### **6.3 Documentation Update**
- Update configuration documentation
- Document new YAML structure
- Document environment variables that remain

#### **6.4 Testing Steps**:
1. **Full system test**: Test all functionality end-to-end
2. **Performance test**: Verify no performance degradation
3. **Configuration test**: Test all YAML configuration options
4. **Cleanup**: Remove debug logging
5. **Documentation**: Update docs

---

## 🧪 **Testing Strategy**

### **For Each Phase**:

#### **Pre-Test Checklist**:
- [ ] Current functionality works correctly
- [ ] Backend logs show expected configuration
- [ ] Health endpoint returns correct values
- [ ] Admin panel shows correct information

#### **Post-Test Checklist**:
- [ ] All functionality still works
- [ ] Backend logs show YAML configuration loading
- [ ] Health endpoint shows updated values
- [ ] Admin panel shows correct information
- [ ] No errors in browser console
- [ ] No errors in backend logs

#### **Rollback Plan**:
- Keep backup of original docker-compose.yml
- Each phase can be rolled back independently
- Test rollback procedure before starting

---

## 📊 **Success Metrics**

### **Phase 1-2 (Remove Duplicates)**:
- ✅ No duplicate configuration between environment variables and YAML
- ✅ Backend reads all settings from YAML
- ✅ Health endpoint shows YAML values

### **Phase 3-4 (Add Missing Config)**:
- ✅ All configurable values are in YAML
- ✅ Only sensitive data remains as environment variables
- ✅ Backend handles missing YAML gracefully

### **Phase 5-6 (Frontend Integration)**:
- ✅ Frontend reads configuration from backend
- ✅ Admin panel uses configurable values
- ✅ Debug page uses configurable limits
- ✅ All functionality works correctly

---

## 🚨 **Risk Mitigation**

### **Configuration Loading Issues**:
- Add comprehensive error handling
- Provide sensible defaults for missing YAML values
- Add debug logging during development

### **Frontend-Backend Mismatch**:
- Test frontend configuration loading thoroughly
- Add fallback values for missing configuration
- Verify all components handle missing config gracefully

### **Performance Impact**:
- Monitor configuration loading performance
- Cache configuration values where appropriate
- Test with large configuration files

---

## 📅 **Estimated Timeline**

- **Phase 1**: 1-2 hours
- **Phase 2**: 1-2 hours  
- **Phase 3**: 2-3 hours
- **Phase 4**: 2-3 hours
- **Phase 5**: 3-4 hours
- **Phase 6**: 1-2 hours

**Total**: 10-16 hours

---

## 🎯 **Current Status**

**Status**: Implementation Complete ✅
**Next Action**: All phases completed successfully
**Last Updated**: 2025-08-31

---

## 📝 **Implementation Notes**

### **Environment Variables to Keep**:
- `LLM_API_KEY` - Sensitive data
- `SECRET_KEY` - Sensitive data  
- `ADMIN_PASSWORD` - Sensitive data
- `APP_ENV` - Environment selection
- `DOMAIN` - Domain configuration (until moved to YAML)

### **Environment Variables to Remove**:
- `LLM_TIMEOUT` - Use YAML: `config/llm.yaml` → `api_configuration.timeout`
- `LLM_PROVIDER` - Use YAML: `config/llm.yaml` → `provider.name`
- `LLM_MODEL` - Use YAML: `config/llm.yaml` → `provider.model`
- `RATE_LIMIT_PER_SESSION` - Use YAML: `config/auth.yaml` → `rate_limiting.requests_per_session_per_hour`
- `RATE_LIMIT_PER_HOUR` - Use YAML: `config/auth.yaml` → `rate_limiting.global_requests_per_hour`
- `LOG_LEVEL` - Add to YAML: `config/auth.yaml` → `session_management.log_level`
- `MAX_CONCURRENT_USERS` - Add to YAML: `config/auth.yaml` → `session_management.max_concurrent_users`
- `VITE_BACKEND_URL` - Add to YAML: `config/deployment.yaml` → `frontend.backend_url`

---

## 🔄 **Progress Tracking**

### **Phase 1**: ✅ Complete
### **Phase 2**: ✅ Complete  
### **Phase 3**: ✅ Complete
### **Phase 4**: ✅ Complete
### **Phase 5**: ✅ Complete
### **Phase 6**: ✅ Complete

**Overall Progress**: 100% Complete
