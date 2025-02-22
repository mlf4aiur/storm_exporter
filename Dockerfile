ARG PYTHON_IMAGE=python:3-alpine
FROM ${PYTHON_IMAGE} AS build

# Install Python dependencies
RUN pip install --no-cache-dir apscheduler prometheus-client requests

# Create a non-root user and application directory
RUN adduser -D app && mkdir -p /app && chown -R app:app /app

# Set working directory
WORKDIR /app

# Copy application files
COPY storm_exporter.py /app/storm_exporter.py

# Change ownership and set execution permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose Prometheus metrics port
EXPOSE 9800

# Run the application
CMD ["python", "/app/storm_exporter.py"]
