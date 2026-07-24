# Ollama Runtime for EasyBDD (Docker Compose)

This setup is optimized for reproducible EasyBDD testing and AI-assisted test authoring.

## Why this runtime

- Reproducible startup behavior (`restart: unless-stopped`)
- Persistent models (`easybdd_ollama_data` volume)
- Easy model pre-pull for builder and crawler workflows
- Stable endpoint for local host: `http://127.0.0.1:11434`

## 1) Avoid port conflict with Snap-managed Ollama

If Snap Ollama is running on this host, stop/disable it first:

```bash
sudo systemctl disable --now snap.ollama.listener.service
```

To revert later:

```bash
sudo systemctl enable --now snap.ollama.listener.service
```

## 2) Start Ollama container

From this folder:

```bash
cd deploy/ollama
docker compose up -d
```

## 3) Preload models used by EasyBDD

```bash
docker compose --profile init run --rm model-init
```

Recommended baseline (CPU-friendly):

- `qwen2.5-coder:7b` for crawler + MCP tools
- `qwen2.5-coder:7b` (or a stronger chat model) for builder chat

## 4) Set EasyBDD env vars

Add or update these in the project `.env`:

```env
OLLAMA_BASE_URL=http://127.0.0.1:11434

CRAWLER_AI_PROVIDER=ollama
CRAWLER_AI_MODEL=qwen2.5-coder:7b
OLLAMA_NUM_CTX=4096
OLLAMA_TIMEOUT=1200
OLLAMA_MAX_SNAPSHOT_CHARS=12000

BUILDER_CHAT_MODEL=qwen2.5-coder:7b
BUILDER_CHAT_NUM_CTX=8192
BUILDER_CHAT_MAX_TOKENS=350
BUILDER_CHAT_KEEP_ALIVE=30m
```

## 5) Verify runtime

```bash
curl -sS http://127.0.0.1:11434/api/tags
```

You should see JSON with the pulled models.

## 6) If EasyBDD runs in a container

Use one of these patterns:

- Same Docker network and service DNS: `http://ollama:11434`
- Host access from container: `http://host.docker.internal:11434` (add host-gateway mapping on Linux if needed)

## Operational commands

```bash
# Follow logs
docker compose logs -f ollama

# Restart runtime
docker compose restart ollama

# Stop runtime
docker compose down
```
