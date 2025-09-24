# Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Run OpenCV in headless mode 
ENV QT_QPA_PLATFORM=offscreen

# system dependencies for OpenCV & video processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements 
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Cfolders for uploads and outputs
RUN mkdir -p uploads outputs

# Expose FastAPI port
EXPOSE 8000


# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
