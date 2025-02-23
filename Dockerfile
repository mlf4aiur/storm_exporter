ARG PYTHON_IMAGE=python:3-alpine
FROM ${PYTHON_IMAGE} AS build

# Set working directory
WORKDIR /app

# Copy application files and requirements.txt to /app/
COPY storm_exporter.py requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and application directory
RUN adduser -D app && mkdir -p /app && chown -R app:app /app

# Change ownership and set execution permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose Prometheus metrics port
EXPOSE 9800

# Run the application
CMD ["python", "/app/storm_exporter.py"]
