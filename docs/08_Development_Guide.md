# Development Guide
## Memo AI Coach

**Document ID**: 08_Development_Guide.md
**Document Version**: 1.0
**Last Updated**: Phase 9
**Status**: Draft

---

## 1.0 Coding Principles
Derived from project AGENTS guidelines:
- Favor simplicity and readability over abstraction.
- Each module serves a single responsibility.
- Provide docstrings and inline comments for educational clarity.
- Avoid editing `devspecs/` documents; `docs/` now acts as source of truth.
- Follow PEP 8 style with 4-space indentation and descriptive variable names.

## 2.0 Repository Structure
```
backend/       FastAPI service
vue-frontend/  Vue.js reactive interface
config/        YAML configuration files
tests/         Test suites
docs/          Comprehensive project documentation
```

## 3.0 Backend Development
- Entry point: `backend/main.py`.
- Data models in `backend/models/entities.py` reflect tables created by `init_db.py`.
- Services in `backend/services/` handle configuration, authentication and LLM integration.
- Use `evaluate_text_with_llm` for all evaluations; it handles prompt generation and error management.
- Error responses should use the standard `{data: null, meta, errors}` schema defined in API documentation.
- Add new endpoints by extending `backend/main.py` and documenting them in `docs/05_API_Documentation.md`.

## 4.0 Frontend Development
- Entry point: `vue-frontend/src/main.js`.
- `vue-frontend/src/services/api.js` provides HTTP client with automatic authentication headers.
- `vue-frontend/src/stores/auth.js` manages authentication state using Pinia.
- `vue-frontend/src/router/index.js` handles route-based navigation and access control.
- Follow Vue 3 Composition API patterns for reactive components.
- Views should be added under `vue-frontend/src/views/` with corresponding routes.
- Components should be added under `vue-frontend/src/components/` with clear, commented functions.
- **Layout Component**: Use Layout wrapper in view components when navigation is needed.
- **Tailwind CSS**: Use v3.4.17 (stable) with proper PostCSS configuration.
- **Authentication Flow**: Login redirects to `/text-input`, logout redirects to `/`.
- **Admin Access**: Conditional menu items based on `isAdmin` status.

### 4.1 Debug and Admin Component Development
Debug and admin components follow specific patterns for consistency and maintainability:

#### Component Structure
- **Location**: Debug components in `vue-frontend/src/components/debug/`
- **Location**: Admin components in `vue-frontend/src/components/admin/`
- **Naming**: Use descriptive names ending with `.vue` (e.g., `ApiHealthTesting.vue`)
- **Layout**: Consistent white background with rounded borders and proper spacing

#### Common Patterns
- **Status Indicators**: Use color-coded badges (green=healthy, red=error, blue=testing, gray=unknown)
- **Loading States**: Show spinners during async operations with disabled buttons
- **Error Handling**: Display errors with copy-to-clipboard functionality for debug info
- **Tooltips**: Use hover tooltips for detailed information display
- **Responsive Design**: Grid layouts that adapt to different screen sizes

#### API Integration
- **Standardized Responses**: All components handle `{data, meta, errors}` response format
- **Authentication**: Include `X-Session-Token` header for all admin/debug requests
- **Error Display**: Show detailed error information with debug context
- **Response Preview**: Display truncated responses with full view on hover

#### Debug Component Features
- **ApiHealthTesting**: Comprehensive endpoint testing with evaluation testing integration
- **SystemDiagnostics**: System health monitoring with real-time updates
- **PerformanceMonitoring**: Response time tracking and system resource monitoring
- **DevelopmentTools**: Various debugging utilities and development aids

#### Admin Component Features
- **HealthStatus**: System health overview and service status monitoring
- **ConfigValidator**: YAML configuration file management with validation
- **UserManagement**: User account creation, management, and role assignment
- **SessionManagement**: Session creation, refresh, and management

#### Last Evaluation Page Development
- **Location**: `vue-frontend/src/views/LastEvaluation.vue`
- **Purpose**: Dedicated page for viewing raw LLM evaluation data
- **Access Control**: Admin-only access with proper route protection
- **Component Integration**: Hosts LastEvaluationsViewer component with Layout wrapper
- **Navigation**: Integrated with main navigation menu for admin users

#### Copyright Footer Implementation
- **Universal Footer**: All pages include consistent "© Copyright FGS" footer
- **Layout Integration**: Footer added to Layout component for authenticated pages
- **Standalone Pages**: Custom footer implementation for Home and Login pages
- **Styling**: Consistent design with white background, gray border, and centered text
- **Responsive Design**: Footer adapts to different page layouts and screen sizes
- **Accessibility**: Uses semantic HTML `<footer>` tag for screen readers

#### Dynamic Framework Injection Development
- **Backend Integration**: Framework content dynamically loaded from `config/rubric.yaml`
- **LLM Service Methods**: `_get_frameworks_content()` and `_get_framework_application_guidance()`
- **Prompt Enhancement**: Framework content injected into LLM prompts at runtime
- **Configuration-Driven**: Framework changes take effect immediately without restarts
- **Validation**: Framework content validated during prompt generation
- **Fallback Handling**: Graceful handling if framework content is missing

#### Testing Requirements
- **Manual Testing**: All debug and admin components require manual testing
- **Authentication Testing**: Verify proper admin access control
- **Error Simulation**: Test error handling and display functionality
- **Performance Testing**: Verify response time tracking and monitoring
- **UI Testing**: Test responsive design and user interactions

## 5.0 Configuration & Secrets
- Never commit API keys or passwords. Use environment variables or `.env`.
- Configuration editing should go through admin API or `config_manager.py` to ensure validation and backups.
- When adding new configuration keys, update both `docs/04_Configuration_Guide.md` and validation logic.

## 5.1 Frontend Configuration
- **Tailwind CSS**: Use v3.4.17 (stable) for production. Avoid v4.x (beta) versions.
- **PostCSS**: Configure with `tailwindcss` plugin (not `@tailwindcss/postcss`).
- **Build Process**: Use `npm install` instead of `npm ci` for better dependency management.
- **CSS Classes**: All components use Tailwind classes for consistent styling.

## 6.0 Testing
- Tests reside in `tests/` and cover environment, integration, performance and security.
- `tests/run_quick_tests.py` runs fast checks; `tests/run_production_tests.py` includes performance suite.
- New features require corresponding unit or integration tests.
- Test files mirror module paths to simplify discovery.

## 7.0 Changelog Standards

### 7.1 Changelog File Location
- **Primary Changelog**: `devlog/vue_implementation_changelog.md`
- **Purpose**: Track all significant changes, fixes, and enhancements to the Vue frontend implementation
- **Audience**: Developers, stakeholders, and future maintainers

### 7.2 Structure Standards
- **Reverse Chronological Order**: Most recent changes first
- **Consistent Date Format**: `[YYYY-MM-DD]` for all entries
- **Clear Entry Types**: Use standardized prefixes (Added, Changed, Deprecated, Removed, Fixed, Security)
- **Concise Headlines**: One-line summaries that clearly describe the change
- **Detailed Descriptions**: Provide context, impact, and technical details when needed

### 7.3 Content Guidelines
- **User-Focused**: Explain what changed from the user's perspective
- **Technical Accuracy**: Include specific file paths, code examples, and technical details
- **Impact Assessment**: Describe the effect on functionality, performance, or user experience
- **Testing Information**: Document verification steps and test results
- **Breaking Changes**: Clearly mark and explain any breaking changes

### 7.4 Entry Format Template
```markdown
### [YYYY-MM-DD] Brief Description of Change

**Type**: Fixed/Added/Changed/Deprecated/Removed/Security  
**Impact**: User Experience/UI/UX/Security/Performance/Developer Experience  
**Priority**: High/Medium/Low  

**Issue**: Clear description of the problem or enhancement need.

**Root Cause**: Technical explanation of why the issue occurred (for fixes).

**Solution**: Detailed description of the implemented solution.

**Files Modified**:
- `path/to/file.ext` - Specific change made

**Testing**: Description of verification steps and results.

**Code Change** (if applicable):
```javascript
// Before: Previous implementation
oldCode();

// After: New implementation
newCode();
```
```

### 7.5 Formatting Standards
- **Consistent Markdown**: Use proper heading hierarchy and formatting
- **Code Blocks**: Include relevant code examples with syntax highlighting
- **File References**: Use backticks for file paths and technical terms
- **Status Indicators**: Use ✅/❌/🔧/🔍 symbols for quick visual scanning
- **Categorization**: Group related changes and use clear section headers

### 7.6 Quality Criteria
- **Completeness**: Include all significant changes with sufficient detail
- **Clarity**: Write in clear, professional language
- **Traceability**: Link changes to issues, phases, or requirements
- **Maintainability**: Structure for easy updates and navigation
- **Historical Value**: Preserve context for future reference

### 7.7 When to Update Changelog
- **All bug fixes** with clear issue description and solution
- **New features** with user impact and technical details
- **UI/UX changes** affecting user experience
- **Security updates** with impact assessment
- **Performance improvements** with measurable results
- **Breaking changes** with migration guidance
- **Configuration changes** affecting deployment or behavior

### 7.8 Changelog Maintenance
- **Regular Updates**: Update changelog with each significant change
- **Version Tracking**: Maintain document history and version numbers
- **Cross-References**: Link to related documentation, issues, or pull requests
- **Review Process**: Ensure accuracy and completeness before finalizing entries

## 8.0 Contribution Workflow
1. Review relevant docs in this directory before coding.
2. Implement changes in small, well-documented commits.
3. Update changelog in `devlog/vue_implementation_changelog.md` following the standards in section 7.0.
4. Add or update tests when modifying behavior.
5. Run appropriate test suites and document results in pull requests.

## 9.0 References
- `AGENTS.md`
- `tests/README.md`
- `devlog/vue_implementation_changelog.md`
