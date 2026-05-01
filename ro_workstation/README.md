# RO Workstation

An offline-first regional office workstation for Indian Public Sector Bank operations, now refactored into layered architecture for maintainability and production readiness.

## Architecture

The project is now organized into clearly separated layers:

```text
core/             config, security, logging, path utilities
domain/           Pydantic schemas and domain enums
application/      business services and use cases
infrastructure/   repositories, loaders, LLM adapters
interface/        Streamlit pages, components, theme, state
app/              legacy compatibility shims and existing assets
tests/            unit and integration tests
```

## Key Improvements

- Centralized config loading with caching in `core/config/config_loader.py`
- Role/session/auth handling in `core/security`
- Repository pattern for JSON, Excel, and SQLite-backed workloads
- Consolidated MIS ingestion and analytics in `application/use_cases/mis`
- Consolidated knowledge indexing/search/QA in `application/use_cases/knowledge`
- Routed Streamlit interface with reusable primitives and structured state
- Added global search, activity timeline, notifications-friendly dashboard, and Excel export flows
- Added lint/tooling config for `black`, `isort`, and `flake8`

## Running Locally

```bash
python -m streamlit run app.py
```

## Docker

```bash
docker compose up --build
```

The container includes a health check against Streamlit's internal health endpoint.

## Offline Preparation

On an internet-connected machine:

```bash
pip download -r requirements.txt -d ./wheels/
ollama pull mistral
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('assets/models/all-MiniLM-L6-v2')"
docker compose build
docker save ro-workstation-app ollama/ollama | gzip > ro-workstation.tar.gz
```

On the internal network:

```bash
docker load < ro-workstation.tar.gz
docker compose up -d
```

## Testing

```bash
python -m pytest
```

If `pytest` is not available in your environment, the tests can also be run with:

```bash
python -m unittest discover -s tests
```
