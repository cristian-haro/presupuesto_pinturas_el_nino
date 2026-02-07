FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for fonts
RUN apt-get update && apt-get install -y fonts-liberation && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
