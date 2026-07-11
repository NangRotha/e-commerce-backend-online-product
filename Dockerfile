# ប្រើ Python 3.9 ជារូបភាពមូលដ្ឋាន
FROM python:3.9-slim

# កំណត់ Working Directory
WORKDIR /app

# ដំឡើងបណ្ណាល័យប្រព័ន្ធដែលត្រូវការ
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ចម្លង requirements.txt ហើយដំឡើង dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ចម្លងកូដទាំងអស់ទៅក្នុង container
COPY . .

# បង្ហាញ Port 8000
EXPOSE 8000

# រត់កម្មវិធីជាមួយ uvicorn (ប្រើ 0.0.0.0 ដើម្បីឱ្យ FastAPI Cloud ទទួលស្គាល់)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]