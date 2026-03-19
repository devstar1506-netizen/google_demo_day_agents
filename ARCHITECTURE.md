# Multi-Agent Framework Architecture

This document describes the high-level architecture of the intelligent agent system.

## 🏗️ System Overview

The system follows a hierarchical orchestration pattern, where a **Main Agent** manages several specialized agents, each backed by either a local LLM or a cloud-based API.

```mermaid
graph TD
    User((User)) -->|Input Task| WebUI[Glassmorphism Frontend]
    WebUI -->|REST API POST| Server[Python Backend Server]
    
    subgraph "Agent Framework"
        Server -->|Orchestrate| MainAgent[Main Agent]
        MainAgent -->|Delegate| Coder[Python Coder Agent]
        MainAgent -->|Delegate| Security[Security Auditor Agent]
        MainAgent -->|Delegate| Standards[PEP8 Standards Agent]
        MainAgent -->|Delegate| DevOps[DevOps Deployment Agent]
    end

    subgraph "Intelligence Layer"
        Coder & Security & Standards & DevOps -->|1. Try Local| Ollama[Ollama / CodeLlama]
        Coder & Security & Standards & DevOps -->|2. Fallback| OpenAI[OpenAI / GPT-4]
        Coder & Security & Standards & DevOps -->|3. Fallback| Mock[Simulated Mock Logic]
    end

    subgraph "External Integrations"
        Security & Standards -->|GH PR Review| GHCLI[GitHub CLI / gh]
        DevOps -->|Sync/Push| Git[Git / GitHub Remote]
    end
```

## 🛠️ Key Components

1.  **Frontend**: A modern, responsive dashboard built with Vanilla HTML/CSS/JS, featuring real-time terminal logging.
2.  **Backend Server**: A zero-dependency Python server handling static file serving and task routing.
3.  **Agents**: Abstracted Python classes that load skills dynamically from Markdown files.
4.  **Local LLM**: Integrated Ollama support for offline, private, and cost-free code analysis.
5.  **GitHub CLI**: Automated Pull Request fetching, diffing, and commenting.
