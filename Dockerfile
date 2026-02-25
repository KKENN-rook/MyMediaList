FROM python:3.12-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Specifies Working Directory
WORKDIR /app

# Linux Package updates (Unnecessary if none of the python need C compilation)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \  
#   && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 5000

# Run App 
CMD ["flask", "--app", "mymedialist", "run", "--host=0.0.0.0", "--port=5000"]