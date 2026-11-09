<div align="center">

# 🚀 IntelliSupport AI

### Intelligent Multi-Agent Customer Support Platform

An AI-powered customer support platform built with **Python, FastAPI, LangGraph, Model Context Protocol (MCP), and Retrieval-Augmented Generation (RAG)** to automate customer queries, manage support tickets, retrieve knowledge, and coordinate intelligent support workflows.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![MCP](https://img.shields.io/badge/MCP-Integration-purple)
![RAG](https://img.shields.io/badge/RAG-Knowledge%20Retrieval-green)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)

</div>

---

## 📌 Project Overview

**IntelliSupport AI** is an intelligent customer support automation system designed to improve customer experience through AI-assisted workflows.

Traditional customer support systems often depend on manual ticket handling, repetitive responses, and time-consuming query resolution.

IntelliSupport AI addresses these challenges through a multi-step AI workflow that classifies customer queries, retrieves relevant knowledge, generates support responses, and manages support tickets.

The platform combines modern AI technologies with backend engineering to create a scalable foundation for intelligent customer support.

## ✨ Key Features

### 🤖 1. Multi-Agent AI Workflow
- Built using LangGraph.
- Multiple specialized workflow nodes.
- Query classification and processing.
- Knowledge retrieval and response generation.
- Supervisor workflow coordination.

### 🔌 2. Model Context Protocol (MCP)
- Separate MCP server integration.
- Knowledge-base search tools.
- Support ticket creation tools.
- Open ticket listing tools.
- Standardized tool access for MCP-compatible clients.

### 🧠 3. Retrieval-Augmented Generation (RAG)
- Knowledge-base search.
- Document-based information retrieval.
- TF-IDF-based retrieval.
- Optional semantic retrieval using Sentence Transformers.
- Context-aware support response generation.

### 🔐 4. Authentication & Authorization
- User registration and login.
- JWT-based authentication.
- Password hashing.
- Role-based access control.
- Customer, Support, and Admin roles.

### 🎫 5. Support Ticket Management
- Create support tickets.
- View available tickets.
- Update ticket information.
- Track ticket status.
- Support and admin permissions.

### 📊 6. Admin Dashboard
- User management.
- Role management.
- Support overview metrics.
- Ticket monitoring.

### ⚡ 7. Real-Time Workflow Updates
- WebSocket-based workflow events.
- Workflow progress information.
- Live client communication.

### ☁️ 8. Cloud & DevOps Integration
- Docker containerization.
- Docker Compose configuration.
- AWS Terraform starter infrastructure.
- Automated testing with Pytest.
- SQLite and PostgreSQL support.

---

## 🏗️ System Architecture

```text
                 CUSTOMER / SUPPORT USER
                           |
                           v
                  WEB APPLICATION UI
                           |
                           v
                    FASTAPI BACKEND
                           |
                  JWT AUTHENTICATION
                           |
                           v
                  LANGGRAPH WORKFLOW
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
     CLASSIFICATION   KNOWLEDGE RAG    TICKET HANDLING
          |                |                |
          v                v                v
     QUERY ANALYSIS   KNOWLEDGE BASE   DATABASE
          |                |                |
          +----------------+----------------+
                           |
                           v
                 RESPONSE GENERATION
                           |
                           v
                   CUSTOMER RESPONSE

              SEPARATE MCP SERVER
                      |
           +----------+----------+
           |          |          |
       Knowledge   Create     List Open
        Search     Ticket      Tickets
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| AI Orchestration | LangGraph |
| AI Integration | LangChain Core |
| AI Architecture | Multi-Agent Workflow |
| Agent Interoperability | Model Context Protocol |
| Knowledge Retrieval | RAG, TF-IDF |
| Semantic Search | Sentence Transformers (optional) |
| Authentication | JWT, bcrypt |
| Database | SQLite, PostgreSQL |
| Real-Time Communication | WebSockets |
| Containerization | Docker, Docker Compose |
| Cloud Infrastructure | AWS, Terraform |
| Testing | Pytest |

## 📂 Project Structure

```text
IntelliSupport-AI/
│
├── app/
│   ├── agents.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── rag.py
│   ├── schemas.py
│   ├── security.py
│   │
│   └── static/
│       └── index.html
│
├── mcp_server/
│   └── server.py
│
├── infra/
│   └── terraform/
│
├── scripts/
│   └── create_admin.py
│
├── tests/
│
├── docs/
│   └── SECURITY.md
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.11+
- Git
- pip
- Docker (optional)

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/IntelliSupport-AI.git
```

```bash
cd IntelliSupport-AI
```

### Step 2: Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure your environment variables, including a secure application secret key and database URL.

Never upload API keys, passwords, or secret credentials to GitHub.

### Step 5: Run Application

```bash
uvicorn app.main:app --reload
```

### Step 6: Open Application

| Service | URL |
|---|---|
| Web Application | http://127.0.0.1:8000 |
| API Documentation | http://127.0.0.1:8000/docs |
| Health Check | http://127.0.0.1:8000/api/health |

---

## 🐳 Run Using Docker

Build and start the application:

```bash
docker compose up --build
```

Stop the application:

```bash
docker compose down
```

The application will be available at:

```text
http://localhost:8000
```

## 🔌 MCP Server Integration

IntelliSupport AI includes a separate MCP server that exposes support-related tools to compatible MCP clients.

Available tools:

| MCP Tool | Description |
|---|---|
| `search_knowledge` | Searches the knowledge base |
| `create_support_ticket` | Creates a customer support ticket |
| `list_open_tickets` | Retrieves open support tickets |

Run the MCP server:

```bash
python -m mcp_server.server
```

The included server uses stdio transport. Configure an MCP-compatible client to launch it locally.

## 🔗 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get user profile |
| GET | `/api/knowledge` | Get knowledge content |
| GET | `/api/knowledge/search?q=...` | Search knowledge |
| POST | `/api/chat` | Submit customer query |
| GET | `/api/tickets` | Get tickets |
| POST | `/api/tickets` | Create ticket |
| PATCH | `/api/tickets/{ticket_id}` | Update ticket |
| GET | `/api/admin/overview` | Admin overview |
| GET | `/api/admin/users` | List users |
| PATCH | `/api/admin/users/{user_id}/role` | Update user role |
| GET | `/api/health` | Health check |
| WS | `/ws/chat` | Workflow event connection |

For detailed request and response schemas, open the FastAPI Swagger documentation at `/docs`.

## 🧪 Automated Testing

Run the test suite:

```bash
pytest -q
```

Tests should be executed in your configured development environment before deployment.

## ☁️ AWS Deployment

The project includes starter Terraform configuration for exploring AWS infrastructure deployment.

Potential deployment architecture:

```text
             INTERNET
                |
                v
        AWS LOAD BALANCER
                |
                v
          ECS FARGATE
                |
                v
       INTELLISUPPORT AI API
                |
          +-----+------+
          |            |
          v            v
       DATABASE    AI SERVICES
```

Before production deployment, configure and validate:

- AWS IAM permissions.
- Private networking.
- HTTPS and SSL certificates.
- Secure environment variables.
- Managed database and backups.
- Logging and monitoring.
- Rate limiting and application security.

The Terraform configuration is a starter, not a complete production deployment.

## 🔒 Security

The project includes foundational security features:

- JWT authentication.
- Password hashing.
- Role-based authorization.
- Environment-based configuration.
- Protected API endpoints.

Additional security reviews and production controls are required before handling real customer information.

## 🚀 Future Enhancements

- Advanced autonomous AI agents.
- Improved hybrid and vector-based RAG.
- Human-in-the-loop approval.
- Email and WhatsApp support integration.
- Advanced analytics dashboard.
- Customer sentiment analysis.
- Automated ticket prioritization.
- CI/CD pipeline.
- Production AWS deployment.
- AI response evaluation and monitoring.

## 🎯 Project Objectives

The main objectives of IntelliSupport AI are:

1. Reduce repetitive manual customer support tasks.
2. Improve customer query resolution.
3. Demonstrate multi-agent workflow orchestration.
4. Integrate AI tools through MCP.
5. Retrieve relevant information using RAG.
6. Build secure backend services with FastAPI.
7. Explore containerization and cloud deployment.

## 👨‍💻 Author

**Himanshu Chahar**

B.Tech Computer Science & Engineering

**Areas of Interest:**
- Artificial Intelligence
- Agentic AI
- Cloud Computing
- DevOps Engineering
- Backend Development
- AI Automation

## 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for details.

---

<div align="center">

### ⭐ IntelliSupport AI

**Building Smarter Customer Support with AI, Automation & Cloud Technology.**

If you find this project interesting, consider giving the repository a star!

</div>
