# RAG ChatBot - Wine Pairing Assistant

An AI-powered wine pairing chatbot that leverages Retrieval-Augmented Generation (RAG) to recommend wines based on food and cuisine. Built with Streamlit, Ollama, and Qdrant vector database.

## Features

- **AI-Powered Recommendations**: Uses Mistral LLM via Ollama for intelligent wine pairing suggestions
- **Sommelier Expertise**: Trained to provide sommelier-level wine pairing advice
- **Vector Database Search**: Qdrant for efficient semantic search of wine recommendations
- **Wine Database**: SQLite database with wine names and purchase links
- **Interactive Chat UI**: Streamlit-based chat interface for seamless user interaction

## Architecture

### Components

1. **Streamlit Frontend** (`app/main.py`) - Interactive chat interface on port 8501
2. **Ollama LLM** - Local Mistral model for generating recommendations
3. **Qdrant Vector Database** - Semantic search for wines on port 6333
4. **SQLite Database** - Wine database with product links

### Workflow

1. User enters a dish or cuisine name
2. LLM generates wine pairing recommendations
3. Qdrant searches the vector database for matching wines
4. Results are enriched with wine links from SQLite
5. Response is displayed in chat interface

## Prerequisites

- Docker and Docker Compose
- For GPU support with Ollama, follow [these steps](https://hub.docker.com/r/ollama/ollama)

## Getting Started

### Quick Start

1. Navigate to the project directory
2. Run the project:
```bash
docker compose up --build
```

### Access the Application

After the services start, access the RAG ChatBot at:
- **Streamlit UI**: [http://localhost:8501/](http://localhost:8501/)
- **Qdrant API**: [http://localhost:6333/](http://localhost:6333/)

## Project Structure

```
ChatBotRAG-1/
├── app/
│   ├── main.py              # Streamlit application
│   ├── Dockerfile           # Docker configuration for app
│   └── requirements.txt      # Python dependencies
├── tools/
│   ├── create_db.py         # Script to create wine database
│   ├── create_embeddings.py # Script to generate vector embeddings
│   ├── download_model.sh    # Script to download Ollama models
│   ├── test.py              # Testing utilities
│   └── requirements.txt      # Tool dependencies
├── docker-compose.yaml      # Container orchestration
└── README.md
```

## Configuration

Services are configured via environment variables in `docker-compose.yaml`:
- `QDRANT_CLIENT`: Qdrant connection URL
- `OLLAMA`: Ollama service URL

## Troubleshooting

## 1) Docker Buildx Permission Error
If you see an error like:
`open ~/.docker/buildx/current: permission denied`

Fix:
```bash
rm -f ~/.docker/buildx/current
```

Then run:
```bash
docker compose build ragchatbot
```

## 2) SSL Certificate Error While Installing Python Packages
If build fails with messages like:
`SSLError: CERTIFICATE_VERIFY_FAILED` or `self-signed certificate in certificate chain`

Cause:
- Your network/proxy may be intercepting TLS certificates.

Fix already applied in `app/Dockerfile`:
- Install `ca-certificates` in the image.
- Use pip trusted hosts for PyPI endpoints.

Rebuild command:
```bash
docker compose build --no-cache ragchatbot
```