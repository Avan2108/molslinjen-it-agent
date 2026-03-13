# Molslinjen IT Support Agent - Implementation Roadmap

## Overview

This document provides a comprehensive roadmap for implementing the Molslinjen IT Support AI Agent. The implementation is divided into 7 phases, each with detailed tasks, acceptance criteria, and testing instructions.

## Phase Summary

| Phase | Name | Key Deliverables | Est. Effort |
|-------|------|------------------|-------------|
| **Foundation** | ✅ Complete | Project structure, types, enums, models, stubs | Done |
| **Phase 1** | Azure Infrastructure | AI Foundry, AI Search, Storage, SDK clients | 12-16 hours |
| **Phase 2** | Authentication | MSAL frontend, JWT validation, RBAC | 14-18 hours |
| **Phase 3** | Semantic Kernel Agents | Triage, PreFilter, IT Support agents | 24-30 hours |
| **Phase 4** | Plugin Integrations | FreshService, Graph, Knowledge plugins | 20-24 hours |
| **Phase 5** | Frontend Components | Chat, Tickets, FAQs, Admin UI | 46-52 hours |
| **Phase 6** | Full Integration | Complete routes, E2E testing | 32-38 hours |
| **Phase 7** | Production | Azure deploy, monitoring, security | 34-40 hours |

**Total Estimated Effort: 182-218 hours (4.5-5.5 weeks with 2 engineers)**

---

## Phase Dependencies

```
Foundation (Done)
     │
     ▼
┌─────────┐
│ Phase 1 │ Azure Infrastructure
└────┬────┘
     │
     ▼
┌─────────┐
│ Phase 2 │ Authentication
└────┬────┘
     │
     ├───────────────┐
     ▼               ▼
┌─────────┐     ┌─────────┐
│ Phase 3 │     │ Phase 5 │ (Can start frontend
│ Agents  │     │ Frontend│  components in parallel)
└────┬────┘     └────┬────┘
     │               │
     ▼               │
┌─────────┐          │
│ Phase 4 │          │
│ Plugins │          │
└────┬────┘          │
     │               │
     └───────┬───────┘
             ▼
       ┌─────────┐
       │ Phase 6 │ Full Integration
       └────┬────┘
            │
            ▼
       ┌─────────┐
       │ Phase 7 │ Production
       └─────────┘
```

---

## Quick Start for Engineers

### Getting Started

```bash
# Clone repository
git clone https://github.com/molslinjen/molslinjen-it-agent.git
cd molslinjen-it-agent

# Backend setup
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
make dev

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your values
npm run dev
```

### Running Tests

```bash
# Backend
cd backend
make test

# Frontend
cd frontend
npm run test
```

### Linting

```bash
# Backend
cd backend
make lint

# Frontend
cd frontend
npm run lint
```

---

## Phase Documentation

Each phase has detailed documentation with:
- Task breakdown with assignees and effort estimates
- Step-by-step implementation instructions
- Code examples and snippets
- Acceptance criteria
- Testing instructions
- Definition of Done

| Document | Description |
|----------|-------------|
| [PHASE-1-AZURE-INFRASTRUCTURE.md](./PHASE-1-AZURE-INFRASTRUCTURE.md) | Azure resource setup, SDK integration |
| [PHASE-2-AUTHENTICATION.md](./PHASE-2-AUTHENTICATION.md) | MSAL, JWT validation, RBAC |
| [PHASE-3-SEMANTIC-KERNEL-AGENTS.md](./PHASE-3-SEMANTIC-KERNEL-AGENTS.md) | AI agents implementation |
| [PHASE-4-PLUGIN-INTEGRATIONS.md](./PHASE-4-PLUGIN-INTEGRATIONS.md) | FreshService, Graph, Knowledge plugins |
| [PHASE-5-FRONTEND-COMPONENTS.md](./PHASE-5-FRONTEND-COMPONENTS.md) | React components |
| [PHASE-6-FULL-INTEGRATION.md](./PHASE-6-FULL-INTEGRATION.md) | E2E integration, route completion |
| [PHASE-7-PRODUCTION.md](./PHASE-7-PRODUCTION.md) | Deployment, monitoring, security |

---

## Team Roles

| Role | Responsibilities |
|------|------------------|
| **Backend Developer** | Python/FastAPI, Semantic Kernel, Plugins, APIs |
| **Frontend Developer** | React/TypeScript, Components, MSAL integration |
| **Infrastructure Engineer** | Azure resources, CI/CD, IaC |
| **Security Engineer** | Security hardening, compliance, audit |
| **QA Engineer** | Testing, E2E tests, load testing |

---

## Key Technologies

### Backend
- **Python 3.12** - Runtime
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Semantic Kernel** - AI orchestration
- **Azure AI Foundry** - LLM inference
- **Azure AI Search** - Knowledge retrieval
- **Azure Table Storage** - Data persistence

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **MSAL** - Authentication

### Infrastructure
- **Azure App Service** - Backend hosting
- **Azure Static Web Apps** - Frontend hosting
- **Azure Key Vault** - Secrets management
- **Application Insights** - Monitoring
- **GitHub Actions** - CI/CD

---

## Definition of Done (All Phases)

Before marking any phase complete:

- [ ] All tasks completed
- [ ] All acceptance criteria met
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] No critical bugs
- [ ] Performance acceptable
- [ ] Security review passed (where applicable)

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Azure AI rate limits | Implement retry logic, caching |
| FreshService API changes | Version lock, adapter pattern |
| Authentication issues | Thorough testing, fallback UI |
| Performance degradation | Load testing, monitoring, scaling plan |
| Data loss | Backup strategy, Table Storage redundancy |

---

## Support

- **Technical Issues**: Create GitHub issue
- **Architecture Questions**: Contact lead engineer
- **Azure Access**: Contact IT infrastructure team
- **FreshService API**: Contact FreshService admin

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-12 | 0.1.0 | Initial foundation setup |
