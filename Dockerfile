# Dockerfile
FROM python:3.11-slim

# កំណត់ Working Directory
WORKDIR /app

# តម្លើង System Dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ចម្លង Requirements និងតម្លើង Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ចម្លងកូដទាំងអស់
COPY . .

# បើក Port 8000
EXPOSE 8000

# រត់ Application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]