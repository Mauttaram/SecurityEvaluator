# Production Dockerfile - No venv needed
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Green Agent
EXPOSE 9010

# Run the Green Agent
CMD ["python", "green_agents/cybersecurity_evaluator.py", "--host", "0.0.0.0", "--port", "9010"]
