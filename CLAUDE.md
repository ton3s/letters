# Claude Context for Insurance Letter Generator

This document captures the complete context of the Insurance Letter Generator project for quick session recovery.

## Project Overview

An enterprise-grade insurance letter drafting application featuring:
- **Multi-Agent AI System**: Three specialized agents (Letter Writer, Compliance Reviewer, Customer Service) collaborate to create professional letters
- **React UI**: Modern, responsive interface with real-time progress tracking and placeholder management
- **Azure Functions API**: Serverless backend with Python and Semantic Kernel
- **SSO Authentication**: Microsoft Entra ID integration with JWT validation
- **Production Ready**: Azure API Management, rate limiting, comprehensive logging
- **CLI Tool**: Command-line interface for testing and automation

## Directory Structure

```
letters/
├── api/                         # Azure Functions Backend
│   ├── function_app.py         # Main Azure Functions app
│   ├── services/               # Backend services
│   │   ├── agent_system.py     # Multi-agent orchestration
│   │   ├── cosmos_service.py   # Database integration
│   │   └── models.py           # Pydantic data models
│   ├── middleware/             # Authentication middleware
│   │   └── auth.py            # JWT validation
│   ├── tests/                  # Comprehensive test suite (80%+ coverage)
│   ├── deployment/             # APIM policies and configs
│   └── local.settings.json     # Local config (gitignored)
├── ui/                         # React Frontend
│   ├── src/
│   │   ├── auth/              # MSAL authentication
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API and local services
│   │   └── App.tsx            # Main app with routing
│   └── .env.local             # Frontend config (gitignored)
├── cli-tool/                   # CLI testing tool
├── docs/                       # Comprehensive documentation
└── setup.sh                    # One-click setup script
```

## Technology Stack

### Frontend
- **React 19.1.0** with TypeScript
- **Tailwind CSS** for styling
- **MSAL React** for authentication
- **React Router** for navigation
- **Heroicons** for icons
- **Nunito font** with State Farm-inspired color scheme

### Backend
- **Python 3.9+** with type hints
- **Azure Functions v4** (HTTP triggers)
- **Semantic Kernel** for multi-agent orchestration
- **Azure OpenAI** (GPT-4)
- **Pydantic** for data validation
- **PyJWT** for token validation
- **Pytest** for testing

### Infrastructure
- **Azure Cosmos DB** for persistence
- **Azure API Management** for production
- **Microsoft Entra ID** for SSO
- **Azure Static Web Apps** for UI hosting

## Key Features Implementation

### 1. Multi-Agent System

The system uses three specialized agents that collaborate through Semantic Kernel:

```python
# Agent roles and approval workflow
- LetterWriter: Creates initial draft, incorporates feedback
- ComplianceReviewer: Checks regulatory compliance
- CustomerServiceReviewer: Ensures customer-friendly tone

# Termination strategy: All agents must approve (max 5 rounds)
```

### 2. Placeholder Management System

Comprehensive placeholder detection and replacement:

```typescript
// Placeholder types: text, date, currency, email, phone, address, name
// Visual indicators: Yellow (unfilled), Green (filled)
// Auto-population from Company Settings
// Inline editing with validation
// Auto-save with 1-second debounce
```

Key placeholder patterns:
- `[Date]`, `[Today's Date]` → Current date
- `[Company Name]`, `[Agent Name]` → From settings
- `[Your Name]` → Agent from form, fallback to settings
- Financial placeholders with currency formatting
- Smart detection avoiding overlaps

### 3. Authentication Flow

```
User → React App → MSAL → Entra ID → JWT Token
                                         ↓
API ← JWT Validation ← API Management ← Request
```

Configuration:
- Frontend: `REACT_APP_AZURE_AD_CLIENT_ID`, `REACT_APP_AZURE_AD_TENANT_ID`
- Backend: `AZURE_AD_CLIENT_ID`, `AZURE_AD_TENANT_ID`
- API Scope: `api://[client-id]/access_as_user`

### 4. UI Component Patterns

```typescript
// Layout with persistent sidebar
<Layout>
  <Sidebar /> // Navigation: Generate, History, Settings
  <main>{children}</main>
</Layout>

// Protected routes
<AuthProvider>
  <ProtectedRoute>
    <Component />
  </ProtectedRoute>
</AuthProvider>

// Loading states with progress messages
<LoadingModal messages={progressMessages} />

// Action organization with dropdown
<DropdownMenu>
  <MenuItem onClick={handleAction} />
</DropdownMenu>
```

### 5. Letter History Management

```typescript
// LocalStorage-based persistence
LetterHistoryService.save(letter)
LetterHistoryService.getAll()
LetterHistoryService.update(id, updates) // For auto-save
LetterHistoryService.delete(id)
```

## API Endpoints

```
GET  /api/health                    # Health check (no auth)
POST /api/draft-letter              # Generate letter (auth required)
POST /api/suggest-letter-type       # AI suggestion for letter type
POST /api/validate-letter           # Validate letter content
```

## Important Patterns and Decisions

### 1. CORS Configuration
```json
// api/local.settings.json
"Host": {
  "CORS": "http://localhost:3000"
}
```

### 2. Progress Messages
```typescript
// Show which agent is working
const progressMessages = [
  { delay: 0, message: 'Initializing letter generation...' },
  { delay: 2000, message: 'Letter Writer agent is drafting your letter...' },
  { delay: 8000, message: 'Compliance Reviewer agent is reviewing...' },
  // etc.
];
```

### 3. Signature Formatting
```typescript
// Ensure proper spacing in letter footer
const formatSignature = (content: string): string => {
  // Add newline before "Sincerely,"
  // Remove extra newlines between signature elements
  // Ensure consistent spacing
};
```

### 4. Company Settings Integration
```typescript
// Auto-populate placeholders from settings
CompanyProfileService.applyToLetter(content, profile, {
  agentName: formData.agent_name // Form overrides default
});
```

### 5. Test Organization
```
api/tests/          # Backend tests (80%+ coverage)
ui/src/**/__tests__/ # Frontend component tests
cli-tool/tests/     # CLI tests
```

## Common Issues and Solutions

### 1. API Endpoint Names
- Correct: `/api/draft-letter` (not `/api/generate-letter`)
- Always include `/api` prefix for Function App routes

### 2. Authentication Errors
- Ensure redirect URI matches exactly (including trailing slashes)
- Token must include correct audience (`api://[client-id]/access_as_user`)
- Backend validates issuer as `https://login.microsoftonline.com/[tenant-id]/v2.0`

### 3. Placeholder Replacement
- Use exact pattern matching (case-insensitive)
- Handle variations: `[Company Name]`, `[Insurance Company Name]`, `[Our Company]`
- Agent name priority: Form input → Company settings → Default

### 4. Mobile UI
- Sidebar close button positioning (no negative margins)
- Responsive grid layouts with Tailwind classes
- Touch-friendly button sizes

### 5. Environment Variables
- Frontend: `.env.local` (prefix with `REACT_APP_`)
- Backend: `local.settings.json` (Azure Functions format)
- Never commit actual credentials

## Development Workflow

### Setup
```bash
./setup.sh                          # One-click setup
cp api/local.settings.json.example api/local.settings.json
cp ui/.env.example ui/.env.local
# Update with your Azure credentials
```

### Running Locally
```bash
# Terminal 1: Storage emulator
azurite --silent

# Terminal 2: Backend
cd api && source ../venv/bin/activate && func start

# Terminal 3: Frontend
cd ui && npm start
```

### Testing
```bash
# Backend
cd api && python tests/run_tests.py --coverage

# Frontend
cd ui && npm test -- --coverage

# CLI
cd cli-tool/tests && python test_conversation.py
```

## Production Deployment

### Azure Resources
1. **Function App**: Python 3.9, Consumption plan
2. **Cosmos DB**: Serverless, partition key `/type`
3. **API Management**: JWT validation, rate limiting
4. **Static Web Apps**: React hosting
5. **Entra ID**: App registration with proper scopes

### Deployment Commands
```bash
# Backend
cd api && func azure functionapp publish [app-name]

# Frontend
cd ui && npm run build
# Deploy to Static Web Apps

# APIM policies
# Apply from api/deployment/apim-policies.xml
```

## Code Style Guidelines

### Python
- Type hints for all functions
- Docstrings for classes and public methods
- Black formatting (100 char limit)
- Comprehensive error handling with logging

### TypeScript/React
- Functional components with TypeScript
- Custom hooks for logic extraction
- Tailwind for styling (no inline styles)
- Proper loading and error states

### General
- No hardcoded values (use environment variables)
- Comprehensive logging at appropriate levels
- Unit tests for business logic
- Integration tests for workflows

## Recent Updates and Decisions

1. **Removed initial login requirement** - Later re-added with SSO
2. **Simplified navigation** - Only Generate, History, Settings
3. **Always save agent conversations** - No checkbox needed
4. **Auto-save placeholder edits** - 1-second debounce
5. **Organized actions in dropdown** - Reduced button clutter
6. **Hide edit button when no placeholders** - Cleaner UI
7. **Agent name spaces in progress** - "LetterWriter" → "Letter Writer"
8. **Comprehensive test coverage** - 80%+ for API
9. **Production-ready auth** - JWT validation, APIM integration
10. **Complete documentation** - Architecture, deployment, local dev guides

## Quick Troubleshooting

### CORS Error
- Check `local.settings.json` has correct CORS settings
- Ensure API is running on port 7071
- Verify frontend uses correct API URL

### Auth Issues
- Check all environment variables are set
- Ensure app registration has correct redirect URI
- Verify API permissions and admin consent

### Placeholder Issues
- Check CompanyProfileService.applyToLetter logic
- Verify regex patterns in PlaceholderService
- Test with various placeholder formats

### Build/Deploy Issues
- Clear node_modules and reinstall
- Check Python virtual environment is activated
- Verify Azure credentials and resource names

## Session Recovery Checklist

When starting a new Claude session:
1. Check current git status and recent commits
2. Verify which environment (local/production)
3. Review any error messages or logs
4. Check TODO list status if applicable
5. Confirm Azure resources are configured
6. Test health endpoint: `curl http://localhost:7071/api/health`

## Key Files Reference

- `api/function_app.py` - API endpoints
- `api/services/agent_system.py` - Multi-agent logic
- `api/middleware/auth.py` - JWT validation
- `ui/src/App.tsx` - Main React app
- `ui/src/services/placeholderService.ts` - Placeholder detection
- `ui/src/components/Letters/LetterDisplay.tsx` - Letter display/edit
- `ui/src/services/companyProfile.ts` - Settings management
- `docs/ARCHITECTURE.md` - System design
- `docs/LOCAL_DEVELOPMENT.md` - Dev setup guide