# ERPNext Production Dockerfile for Digital Ocean App Platform
FROM frappe/erpnext:v15

# Set working directory
WORKDIR /home/frappe/frappe-bench

# Copy custom configurations if any
COPY --chown=frappe:frappe . /home/frappe/frappe-bench/

# Install additional dependencies if needed
USER root
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Switch back to frappe user
USER frappe

# Set environment variables
ENV FRAPPE_USER=frappe
ENV BENCH_PATH=/home/frappe/frappe-bench
ENV PYTHONPATH=/home/frappe/frappe-bench/apps

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/method/ping || exit 1

# Start command
CMD ["bench", "start"]
