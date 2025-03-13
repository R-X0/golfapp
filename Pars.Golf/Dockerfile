FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads
RUN mkdir -p app/static/uploads/clubs \
    app/static/uploads/players \
    app/static/uploads/courses \
    app/static/img

# Set up database
RUN flask db init || true

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]

EXPOSE 5000