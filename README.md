# RAGChatBot

To use GPU in docker for ollama follow these [steps](https://hub.docker.com/r/ollama/ollama)

-- 
# Steps to run  
1 - docker compose up --build (at the RAGChatBot directory level)
2 - # http://localhost:6333/
 - # http://0.0.0.0:8501/
 -# http://localhost:8501/ 

# Troubleshooting

## 1) Docker Buildx Permission Error
If you see an error like:
`open ~/.docker/buildx/current: permission denied`

Fix:
```bash
rm -f ~/.docker/buildx/current
```

Then run:
```bash
docker compose build RAGChatBot
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
docker compose build --no-cache RAGChatBot
```