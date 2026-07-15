# Codesho Sprint Zero

Production-oriented foundation for Codesho. This repository is the test and
coordination environment; promotion to the primary repository happens only
after the quality gate.

## Stack

- Django 5.2 LTS, Django REST Framework, PostgreSQL
- Next.js App Router, TypeScript, RTL
- Redis and Celery
- Nginx same-origin reverse proxy
- Docker Compose for local and initial production parity

## Local startup

1. Copy `.env.example` to `.env` and replace secrets.
2. Run `docker compose up --build`.
3. Open `http://localhost` and `http://localhost/api/schema/swagger-ui/`.

Do not use `.env.example` credentials outside local development. Kubernetes is
intentionally out of scope for the initial deployment.
