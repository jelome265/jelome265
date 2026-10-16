<div align="center">

# JELOME

### System architect · Backend engineer · Rust-first

*Designing backend systems where failure is a first-class concern.*
*If it can fail, I want to know how.*

![Rust](https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white)
![Java](https://img.shields.io/badge/Java_21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Kafka](https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

---

## Reference architecture

Every boundary is treated as something that will fail. The design states how it fails, how it recovers, and who owns the data.

```mermaid
flowchart LR
    C[Client] --> G[Gateway<br/>timeouts · rate limits · authN]
    G --> S1[Service A<br/>bulkhead]
    G --> S2[Service B<br/>bulkhead]
    S1 --> K[(Kafka<br/>retry + DLQ)]
    S2 --> K
    K --> W[Workers<br/>idempotent consumers]
    W --> DB[(PostgreSQL<br/>per-service ownership)]
```

## Featured projects

| Project | What it does | Stack |
|---|---|---|
| **[Sitolo](https://github.com/jelome265/sitolo)** | Business operating system for African SMEs. Connects procurement, inventory, pricing, sales, collections, payment reconciliation, and reporting. Offline-first, tenant-isolated, auditable. | `Rust` `PostgreSQL` `SQLite` `Flutter` `Tauri` |
| **[USORA](https://github.com/jelome265/USORA)** | Multi-tenant KYC and identity verification. Document processing, biometric checks, risk scoring, audit trails. | `Rust` `Axum` `Java 21` `Spring Boot` `Camunda` `Kafka` `PostgreSQL` |
| **[Rustacean](https://github.com/jelome265/Rustacean)** | Reusable Rust engineering workflows for AI coding agents, built on executable checks, CI, and security automation. | `Rust` `Python` `GitHub Actions` `CodeQL` |
| **[Nullwarden](https://github.com/jelome265/nullwarden)** | Zero-knowledge password vault prototype. Local protection with cloud sync, a Rust CLI and core, and a REST backend. | `Rust` `Axum` `PostgreSQL` `Docker` |

## Principles

- **Failure is designed, not discovered.** Timeouts, retries with backoff, idempotency, circuit breakers, bulkheads, graceful degradation.
- **Every piece of data has one owner.** Service-owned databases, consistency chosen per domain.
- **Contracts over coupling.** APIs and events are versioned and treated as public interfaces.
- **Security is the default path.** OAuth2/OIDC, JWT, RBAC, least privilege, encryption at rest, supply-chain checks in CI.
- **Observe what users feel.** OpenTelemetry, SLOs, alerts on symptoms rather than noise.
- **Split by business domain, not by fashion.** No microservices unless the boundary earns them.

## Stack

| Layer | Tools |
|---|---|
| **Primary** | Rust (Axum, Tokio, Cargo) |
| **Enterprise** | Java 21, Spring Boot, Camunda |
| **Data and messaging** | PostgreSQL, Redis, Kafka, SQLite, MinIO/S3 |
| **Infrastructure** | Docker, Docker Compose, GitHub Actions, CodeQL |
| **Clients** | Flutter, Tauri |

## GitHub stats

<p align="center">
  <img height="170" src="https://github-readme-stats.vercel.app/api?username=jelome265&show_icons=true&theme=radical&title_color=61DAFB&icon_color=61DAFB&text_color=C8E1FF&bg_color=0,091519,000000&border_color=3a8296&hide_border=false" />
  <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=jelome265&layout=compact&langs_count=8&theme=radical&title_color=61DAFB&text_color=C8E1FF&bg_color=0,091519,000000&border_color=3a8296&hide_border=false" />
  <img height="170" src="https://streak-stats.demolab.com?user=jelome265&theme=radical&hide_border=false&background=0,000000,091519&currStreakLabel=61DAFB&ring=3a8296&fire=61DAFB&sideLabels=61DAFB" />
</p>

**Public portfolio:** 15 repositories. Forks of upstream projects (Lichess mobile, Tesseract OCR, `gstack`, `agentic-awesome-skills`) are credited to their original authors.

## Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jelome-ngamuti-a6a656281)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:jelomengamuti@gmail.com)

---

<div align="center"><sub>Built to fail gracefully.</sub></div>
