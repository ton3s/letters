# Insurance Letter Generator - Architecture Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [System Architecture](#system-architecture)
4. [Multi-Agent System Design](#multi-agent-system-design)
5. [Component Architecture](#component-architecture)
6. [Data Flow](#data-flow)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Technology Stack](#technology-stack)
10. [Design Decisions](#design-decisions)

## System Overview

The Insurance Letter Generator is a comprehensive application that leverages AI agents to create professional, compliant insurance correspondence. The system uses a multi-agent architecture where specialized AI agents collaborate to draft, review, and approve letters before delivery.

### Key Features

- **Multi-Agent Collaboration**: Three specialized agents work together to ensure quality
- **Compliance Focus**: Built-in compliance checking and approval workflow
- **User-Friendly Interface**: React-based UI with real-time progress tracking
- **Enterprise Security**: SSO with Microsoft Entra ID and API Management
- **Scalable Architecture**: Serverless design using Azure Functions

## Architecture Principles

### 1. **Separation of Concerns**
- Frontend (UI) handles presentation and user interaction
- Backend (API) manages business logic and agent orchestration
- Data layer (Cosmos DB) provides persistence
- Authentication layer (Entra ID) handles security

### 2. **Microservices Approach**
- Each component is independently deployable
- Services communicate through well-defined APIs
- Loose coupling between components

### 3. **Event-Driven Design**
- Asynchronous processing for long-running operations
- Real-time updates through progress tracking
- Non-blocking UI interactions

### 4. **Security First**
- Zero-trust security model
- Token-based authentication
- Rate limiting and API protection

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            User Browser                                  │
│  ┌─────────────────┐                                                   │
│  │   React SPA     │                                                   │
│  │  (TypeScript)   │                                                   │
│  └────────┬────────┘                                                   │
└───────────┼─────────────────────────────────────────────────────────────┘
            │
            │ HTTPS + JWT
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     Azure Cloud Infrastructure                           │
│                                                                         │
│  ┌──────────────────┐        ┌──────────────────┐                     │
│  │  Microsoft       │        │  Azure API       │                     │
│  │  Entra ID       │◀──────▶│  Management      │                     │
│  │  (Auth)         │        │  (Gateway)       │                     │
│  └──────────────────┘        └────────┬─────────┘                     │
│                                       │                                │
│                                       │ Managed API                    │
│                                       ▼                                │
│  ┌──────────────────────────────────────────────────────────┐        │
│  │                  Azure Functions (Python)                  │        │
│  │                                                           │        │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │        │
│  │  │   API       │  │  Agent       │  │  Cosmos DB     │ │        │
│  │  │  Endpoints  │──│  System      │──│  Service       │ │        │
│  │  └─────────────┘  └──────┬───────┘  └────────┬───────┘ │        │
│  │                          │                    │         │        │
│  └──────────────────────────┼────────────────────┼─────────┘        │
│                            │                    │                    │
│                            ▼                    ▼                    │
│  ┌──────────────────────────────────┐  ┌──────────────────┐        │
│  │     Azure OpenAI Service         │  │   Cosmos DB      │        │
│  │  ┌────────┐ ┌────────┐ ┌──────┐│  │   (NoSQL)        │        │
│  │  │Letter  │ │Compli- │ │Cust. ││  │                  │        │
│  │  │Writer  │ │ance    │ │Svc   ││  │  - Letters      │        │
│  │  │Agent   │ │Reviewer│ │Agent ││  │  - Audit Trail  │        │
│  │  └────────┘ └────────┘ └──────┘│  │  - User Data    │        │
│  └──────────────────────────────────┘  └──────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Multi-Agent System Design

### Agent Architecture

The system employs three specialized AI agents that collaborate using the Semantic Kernel framework:

#### 1. **Letter Writer Agent**
- **Role**: Primary content creator
- **Responsibilities**:
  - Draft initial letter based on user requirements
  - Incorporate feedback from other agents
  - Ensure tone and clarity
- **Implementation**: `services/agent_system.py` - `LetterDraftingAgent`

#### 2. **Compliance Reviewer Agent**
- **Role**: Regulatory compliance verification
- **Responsibilities**:
  - Review letters for regulatory compliance
  - Identify missing required disclosures
  - Ensure legal accuracy
- **Implementation**: `services/agent_system.py` - `ComplianceReviewAgent`

#### 3. **Customer Service Agent**
- **Role**: Customer experience optimization
- **Responsibilities**:
  - Evaluate customer-friendliness
  - Check clarity and understanding
  - Ensure appropriate tone
- **Implementation**: `services/agent_system.py` - `CustomerServiceAgent`

### Agent Collaboration Workflow

```
┌─────────────┐
│   Start     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Letter Writer      │     │  User Requirements  │
│  Creates Draft      │◀────│  - Type            │
└──────┬──────────────┘     │  - Context         │
       │                    │  - Customer Info    │
       ▼                    └─────────────────────┘
┌─────────────────────┐
│  Compliance Review  │
│  Checks Regulations │
└──────┬──────────────┘
       │
       ├─── Approved ─────┐
       │                  │
       │                  ▼
       │           ┌─────────────────────┐
       │           │ Customer Service    │
       │           │ Reviews Tone        │
       │           └──────┬──────────────┘
       │                  │
       │                  ├─── Approved ─────┐
       │                  │                  │
       │                  │                  ▼
       │                  │           ┌──────────────┐
       └─── Rejected      └─── Rejected│   Success    │
              │                  │     │  All Approve │
              ▼                  ▼     └──────────────┘
       ┌─────────────────────────┐
       │  Letter Writer          │
       │  Incorporates Feedback  │
       └─────────┬───────────────┘
                 │
                 └──── Loop (Max 5 rounds)
```

### Agent Communication Protocol

Agents communicate through structured messages:

```python
{
    "round": 1,
    "agent": "LetterWriter",
    "action": "draft",
    "content": "Letter content...",
    "status": "WRITER_APPROVED",
    "feedback": []
}
```

### Termination Strategy

The `ApprovalTerminationStrategy` manages the workflow:
- Tracks approval status from all agents
- Implements maximum round limit (5)
- Ensures all agents approve before completion

## Component Architecture

### Frontend Architecture

```
ui/src/
├── App.tsx                 # Main application component
├── auth/                   # Authentication layer
│   ├── AuthProvider.tsx    # Auth context provider
│   ├── authConfig.ts      # MSAL configuration
│   └── ProtectedRoute.tsx # Route protection
├── components/            # Reusable components
│   ├── auth/             # Auth UI components
│   ├── Common/           # Shared components
│   ├── Layout/           # Layout components
│   └── Letters/          # Letter-specific components
├── contexts/             # React contexts
├── hooks/                # Custom React hooks
├── pages/                # Page components
├── services/             # API services
└── types/                # TypeScript definitions
```

### Backend Architecture

```
api/
├── function_app.py        # Azure Functions entry points
├── middleware/           # Middleware components
│   └── auth.py          # JWT authentication
├── services/            # Business logic
│   ├── agent_system.py  # Multi-agent orchestration
│   ├── cosmos_service.py # Database operations
│   └── models.py        # Data models
├── deployment/          # Deployment configs
└── tests/              # Test suite
```

### Key Design Patterns

1. **Service Pattern**: Business logic encapsulated in service classes
2. **Repository Pattern**: Data access through CosmosService
3. **Provider Pattern**: React Context for cross-cutting concerns
4. **Middleware Pattern**: Request processing pipeline
5. **Strategy Pattern**: Agent termination strategies

## Data Flow

### Letter Generation Flow

```
1. User Input (UI)
   ↓
2. API Request (with JWT token)
   ↓
3. Authentication Middleware
   ↓
4. Request Validation
   ↓
5. Agent System Initialization
   ↓
6. Multi-Agent Processing
   ├── Letter Drafting
   ├── Compliance Review
   └── Customer Service Review
   ↓
7. Approval Workflow (iterative)
   ↓
8. Letter Storage (Cosmos DB)
   ↓
9. Response to UI
   ↓
10. Real-time Progress Updates
```

### Data Models

#### Letter Request
```typescript
interface LetterRequest {
  customer_info: CustomerInfo;
  letter_type: LetterType;
  user_prompt: string;
}
```

#### Stored Letter
```typescript
interface StoredLetter {
  id: string;
  type: "letter";
  user_id: string;
  letter_content: string;
  customer_info: CustomerInfo;
  letter_type: LetterType;
  approval_status: ApprovalStatus;
  agent_conversations: AgentConversation[];
  created_at: string;
}
```

## Security Architecture

### Authentication Flow

```
User → Browser → Entra ID → Token → API → Validation → Access
```

### Security Layers

1. **Authentication**: Microsoft Entra ID with OIDC
2. **Authorization**: JWT token validation
3. **API Protection**: Azure API Management
4. **Rate Limiting**: Per-user quotas
5. **Data Encryption**: TLS in transit, encrypted at rest
6. **Input Validation**: Pydantic models and sanitization

### Security Best Practices

- Zero-trust architecture
- Principle of least privilege
- Defense in depth
- Regular security audits
- Automated vulnerability scanning

## Deployment Architecture

### Development Environment

```
Local Development
├── UI: npm start (port 3000)
├── API: func start (port 7071)
├── Storage: Azurite emulator
└── Auth: Entra ID (cloud)
```

### Production Environment

```
Azure Cloud
├── UI: Static Web Apps
├── API: Function App (Consumption)
├── Gateway: API Management
├── Storage: Cosmos DB (Serverless)
├── Auth: Entra ID
└── Monitoring: Application Insights
```

### CI/CD Pipeline

```
GitHub → Actions → Build → Test → Deploy → Azure
```

## Technology Stack

### Frontend
- **Framework**: React 19.1.0 with TypeScript
- **Styling**: Tailwind CSS
- **Authentication**: MSAL React
- **State Management**: React Context + Hooks
- **HTTP Client**: Native Fetch API
- **Build Tool**: Create React App (migration to Vite recommended)

### Backend
- **Runtime**: Python 3.9+
- **Framework**: Azure Functions v4
- **AI Framework**: Semantic Kernel
- **Database**: Azure Cosmos DB
- **Authentication**: PyJWT
- **Testing**: Pytest

### Infrastructure
- **Cloud Provider**: Microsoft Azure
- **API Gateway**: Azure API Management
- **Hosting**: Static Web Apps + Function Apps
- **Database**: Cosmos DB
- **AI Service**: Azure OpenAI

## Design Decisions

### 1. **Why Multi-Agent Architecture?**
- **Separation of Concerns**: Each agent has specialized knowledge
- **Quality Assurance**: Multiple review passes ensure quality
- **Flexibility**: Easy to add new agents or modify behavior
- **Audit Trail**: Complete conversation history for compliance

### 2. **Why Serverless?**
- **Cost Efficiency**: Pay only for execution time
- **Scalability**: Automatic scaling based on demand
- **Maintenance**: No server management required
- **Integration**: Native Azure service integration

### 3. **Why Cosmos DB?**
- **Flexible Schema**: Document model suits varied letter types
- **Global Distribution**: Support for multi-region deployment
- **Serverless Option**: Cost-effective for variable workloads
- **Performance**: Low latency for read operations

### 4. **Why Semantic Kernel?**
- **Agent Orchestration**: Built-in support for multi-agent systems
- **Flexibility**: Easy to switch AI providers
- **Extensibility**: Plugin architecture for custom functionality
- **Microsoft Support**: First-party Microsoft framework

### 5. **Why React + TypeScript?**
- **Type Safety**: Catch errors at compile time
- **Developer Experience**: Excellent tooling and IntelliSense
- **Component Reusability**: Modular architecture
- **Industry Standard**: Large ecosystem and community

## Next Steps

1. **Performance Optimization**
   - Implement caching strategies
   - Add CDN for static assets
   - Optimize bundle size

2. **Enhanced Monitoring**
   - Add custom metrics for agent performance
   - Implement distributed tracing
   - Create dashboards for business metrics

3. **Feature Expansion**
   - Add more letter types
   - Implement batch processing
   - Add email integration

4. **Technical Debt**
   - Migrate from CRA to Vite
   - Implement comprehensive E2E tests
   - Add API versioning strategy