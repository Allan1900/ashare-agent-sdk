# ── Stage 1: Build ────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir build && \
    python -m build --wheel && \
    echo "Build complete"


# ── Stage 2: Runtime ──────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install runtime deps
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl && \
    echo "StockPulse installed"

# Expose ports
EXPOSE 8900 8901

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8900/health')" || exit 1

# Default: start API server
CMD ["stockpulse", "serve"]