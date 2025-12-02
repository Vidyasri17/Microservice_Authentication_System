##############################
# Stage 1: Builder
##############################
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (for pip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (cache optimization)
COPY requirements.txt .

# Install python dependencies
RUN pip install --prefix=/install -r requirements.txt


##############################
# Stage 2: Runtime
##############################
FROM python:3.12-slim AS runtime

WORKDIR /app

# -----------------------------------
# Install system dependencies
# - cron
# - timezone files
# -----------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cron \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------
# Configure timezone to UTC
# -----------------------------------
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/UTC /etc/localtime && echo "UTC" > /etc/timezone

# -----------------------------------
# Copy Python dependencies from builder
# -----------------------------------
COPY --from=builder /install /usr/local

# -----------------------------------
# Copy application code
# -----------------------------------
COPY app/ ./app/
COPY student_private.pem .
COPY student_public.pem .
COPY instructor_public.pem .
COPY request_seed.py .
COPY generate_keys.py .
COPY decrypt_seed.py .
COPY README.md .

# -----------------------------------
# Setup cron directories
# -----------------------------------
RUN mkdir -p /data && chmod 755 /data
RUN mkdir -p /cron && chmod 755 /cron

# Copy cron config file into container (You will create cronjob later)
COPY cronjob /cron/cronjob

# Install cronjob
RUN chmod 0644 /cron/cronjob && crontab /cron/cronjob

# -----------------------------------
# Expose API port
# -----------------------------------
EXPOSE 8080

# -----------------------------------
# Start cron + FastAPI server
# (IMPORTANT: both must run!)
# -----------------------------------
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
