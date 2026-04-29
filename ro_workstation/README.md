# RO Workstation

A comprehensive, offline-first workstation designed for Indian Public Sector Bank Regional Offices.

## Deployment Instructions

### 1. Offline Setup
On an internet-connected machine:
```bash
pip download -r requirements.txt -d ./wheels/
ollama pull mistral # copy ~/.ollama/models to ./ollama_models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2').save('assets/models/all-MiniLM-L6-v2')"
docker compose build
docker save ro-workstation_app ollama/ollama | gzip > ro-workstation.tar.gz
```

### 2. Air-gapped Server Run
On the bank's internal network:
```bash
docker load < ro-workstation.tar.gz
docker compose up -d
```
