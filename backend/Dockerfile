FROM python:3.11-slim

# Run as a dedicated unprivileged user so a compromise in the FastAPI
# process does not grant root in the container.
RUN groupadd --system --gid 1001 rudra \
 && useradd --system --uid 1001 --gid rudra --home-dir /app --shell /sbin/nologin rudra

WORKDIR /app

# Install runtime deps needed for the healthcheck (curl) and keep the
# image otherwise slim. Dependency install is a separate layer from the
# source copy so code changes do not bust the pip cache.
RUN apt-get update \
 && apt-get install --no-install-recommends -y curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=rudra:rudra . .

USER rudra

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
