# AICloud-Innovation Enterprise Framework
# Multi-stage build for production-ready container

# Stage 1: Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY aicloud_innovation/ ./aicloud_innovation/
COPY aws_config.py .
COPY aws_organizations.py .

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV AICLOUD_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from aicloud_innovation import AgentRegistry; print('healthy')"

# Create non-root user for security
RUN useradd -m -u 1000 aicloud && \
    chown -R aicloud:aicloud /app

USER aicloud

# Expose port for agent API (if needed)
EXPOSE 8080

# Default command (can be overridden)
CMD ["python", "-m", "aicloud_innovation"]
