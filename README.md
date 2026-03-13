# Molslinjen IT Support Agent

AI-powered IT support chatbot for Molslinjen employees, built with FastAPI, React, and Azure AI services.

## Project Structure

```
molslinjen-it-agent/
├── .github/workflows/     # CI/CD pipelines
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── api/          # API client
│   │   ├── types/        # TypeScript types
│   │   ├── store/        # Zustand state management
│   │   ├── i18n/         # Internationalization
│   │   └── auth/         # MSAL authentication
│   └── ...
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── agents/       # Semantic Kernel agents
│   │   ├── plugins/      # SK plugins (FreshService, Graph)
│   │   ├── middleware/   # Auth middleware
│   │   ├── models/       # Pydantic models
│   │   ├── storage/      # Table Storage abstraction
│   │   └── main.py       # FastAPI entry point
│   └── tests/
└── docs/                  # Documentation
```

## Prerequisites

- Python 3.12+
- Node.js 20+
- Azure subscription with:
  - Azure AI Foundry
  - Azure AI Search
  - Azure Table Storage
  - Azure AD (Entra ID)
- FreshService account

## Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your values
# Then start the development server
make dev
```

The API will be available at http://localhost:8000

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.local.example .env.local

# Edit .env.local with your values
# Then start the development server
npm run dev
```

The frontend will be available at http://localhost:5173

## Development Commands

### Backend

```bash
make dev        # Start development server
make test       # Run tests with coverage
make lint       # Run ruff + mypy
make format     # Format code with ruff
```

### Frontend

```bash
npm run dev         # Start development server
npm run build       # Build for production
npm run lint        # Run ESLint
npm run typecheck   # Run TypeScript type checking
npm run test        # Run tests
```

## Architecture

### Backend
- **FastAPI** for the REST API
- **Semantic Kernel** for AI agent orchestration
- **Azure AI Foundry** for LLM inference
- **Azure AI Search** for knowledge retrieval
- **Azure Table Storage** for conversation persistence
- **FreshService API** for ticket management

### Frontend
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Zustand** for state management
- **MSAL** for Azure AD authentication
- **i18n** support for EN, DA, SV

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/chat` | Send message to agent |
| `GET /api/v1/chat/sessions` | List user sessions |
| `POST /api/v1/tickets` | Create support ticket |
| `GET /api/v1/tickets` | List user tickets |
| `POST /api/v1/feedback` | Submit feedback |
| `GET /api/v1/faqs` | List FAQs |
| `GET /api/v1/admin/analytics` | Admin dashboard data |

## Environment Variables

See `.env.example` (backend) and `.env.local.example` (frontend) for required configuration.

## License

Proprietary - Molslinjen A/S
