# ─── Stage 1: builder ───────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --upgrade pip --no-cache-dir
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ─── Stage 2: runtime ───────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app/ ./app/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# 1 worker para 256 MB — aumentar apenas se migrar para instância maior
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
