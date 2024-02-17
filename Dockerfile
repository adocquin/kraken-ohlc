# Stage 1: Build and compile environment
FROM python:3.12.2-alpine AS compile-image

# Setup a virtual environment to isolate our package dependencies locally
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image build
FROM python:3.12.2-alpine

# Copy virtual environment from the build stage
COPY --from=compile-image /opt/venv /opt/venv

# Setup environment variable to ensure scripts run in virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Add a non-root user for running the application
RUN adduser -D appuser
USER appuser
WORKDIR /app

# Copy application files
COPY --chown=appuser:appuser krakenohlc/ krakenohlc/
COPY --chown=appuser:appuser __main__.py .

# Run the application
CMD ["python", "-u", "__main__.py"]
