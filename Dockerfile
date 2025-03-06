FROM python:3.9-slim

# Install system dependencies required for mysqlclient
RUN apt-get update && apt-get install -y \
    pkg-config \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first (for Docker caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose port 5000 for Flask
EXPOSE 5000

# By default, run app.py (the SSO + certificate logic)
# CMD ["python", "app/app.py"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.app:app"]
