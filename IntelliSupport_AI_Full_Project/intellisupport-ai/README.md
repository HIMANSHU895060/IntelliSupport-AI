# IntelliSupport AI — Full-Stack Multi-Agent Customer Support

A portfolio-grade, locally runnable implementation demonstrating LangGraph orchestration, an MCP server, retrieval-augmented generation, JWT authentication with roles, real-time workflow events, ticket management, Docker, AWS deployment templates, and automated tests.

> **Deployment note:** This repository contains AWS deployment infrastructure templates. It is not already deployed to your AWS account. You must configure AWS credentials, secrets, domain/TLS, and review the Terraform plan before applying it.

## Architecture

```text
Browser (React-free responsive UI)
   | REST + WebSocket
FastAPI API ── JWT auth / RBAC
   |
   +── LangGraph workflow
   |     Intake → classify → retrieve (RAG) → support → ticket → response → supervisor
   |
   +── RAG service (chunking + hybrid lexical/semantic retrieval + source references)
   |
   +── SQLAlchemy database (SQLite locally; PostgreSQL in Docker/AWS)
   |
   +── MCP server (tools: search knowledge, create ticket, list tickets)
   |
   +── Optional OpenAI-compatible LLM
```

## Included features

- **LangGraph:** actual StateGraph workflow with separate agent nodes and shared state.
- **MCP:** standalone MCP server exposing knowledge search and ticket tools over stdio.
- **RAG:** document chunking, TF-IDF retrieval, optional sentence-transformer semantic retrieval, hybrid scoring, source citations.
- **Authentication:** register/login, hashed passwords, JWT access tokens.
- **RBAC:** customer, support, admin roles; admin-only user management and support/admin ticket operations.
- **Real-time collaboration:** WebSocket emits agent-step events while a workflow runs.
- **Tickets:** automatic creation, priority/status, assignment, ticket history.
- **Admin dashboard:** users, ticket metrics, recent tickets.
- **Docker:** API, PostgreSQL and MCP server compose configuration.
- **AWS:** Terraform starter for VPC, ECS Fargate, ECR, ALB and RDS PostgreSQL. Review before use; costs may apply.
- **Tests:** pytest coverage for auth, RBAC, RAG, chat workflow and tickets.

## Requirements

- Python 3.11+
- Docker Desktop (optional, recommended)
- Node.js is **not** required; the UI is served by FastAPI.

## Run locally on Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

Create your first account using the Register tab. The first registered user is automatically assigned the `admin` role for local bootstrap. Subsequent users are `customer`. Change this behavior before public production use.

## Run with Docker

```bash
docker compose up --build
```

Open `http://localhost:8000`. PostgreSQL is exposed on port 5432 for local development. Change default credentials before any shared deployment.

## Configure an LLM (optional)

Set in `.env`:

```env
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=your-model-name
```

Without an LLM key, the app still runs using deterministic fallback responses. Do not commit `.env`.

## Run the MCP server

The MCP server is a separate process and uses the same database and RAG service:

```bash
python -m mcp_server.server
```

It exposes tools:
- `search_knowledge(query)`
- `create_support_ticket(subject, description, customer_email, priority)`
- `list_open_tickets()`

MCP uses stdio transport. Configure it in your MCP-compatible desktop/client using the absolute path to this repository's Python environment and `mcp_server/server.py`.

## Run tests

```bash
pytest -q
```

Tests use a temporary SQLite database. They do not require an LLM or AWS account.

## API overview

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/tickets`
- `POST /api/tickets`
- `PATCH /api/tickets/{ticket_id}` (support/admin)
- `GET /api/admin/overview` (admin)
- `GET /api/admin/users` (admin)
- `POST /api/chat` (authenticated)
- `WS /ws/chat?token=<JWT>` (authenticated real-time workflow trace)
- `GET /api/knowledge/search?q=...`
- `GET /api/health`

Interactive API docs: `http://127.0.0.1:8000/docs`.

## AWS deployment outline

1. Create an AWS account and configure AWS CLI credentials.
2. Review `infra/terraform/variables.tf` and update values.
3. Build and push the API image to ECR.
4. Configure secrets in AWS Secrets Manager and set `LLM_API_KEY` securely.
5. Run Terraform from `infra/terraform` after reviewing `terraform plan`.
6. Configure DNS and HTTPS certificate for the ALB.
7. Enable backups, logging, alarms, WAF/rate limiting, and least-privilege IAM before production traffic.

The supplied Terraform is a starter baseline, not a security/compliance certification. Validate networking, secrets, costs, scaling, backups and regional requirements for your account.

## Security checklist before production

- Replace all example secrets and database passwords.
- Disable first-user-admin bootstrap and provision admins out-of-band.
- Use HTTPS, secure cookies/token storage, rate limits, CSRF strategy if cookies are introduced, and strict CORS.
- Add email verification, password reset, MFA and account lockout.
- Use a managed secrets store; never commit `.env`.
- Review logs for PII; configure retention and deletion policies.
- Add human approval for refunds, account changes and destructive operations.
- Perform dependency, container and infrastructure scans.

## License

MIT — see `LICENSE`.
