# Use official Python slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Run OpenCV in headless mode to avoid Qt warnings
ENV QT_QPA_PLATFORM=offscreen

# Install system dependencies for OpenCV & video processing
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full project
COPY . .

# Create folders for uploads and outputs
RUN mkdir -p uploads outputs

# Expose FastAPI port
EXPOSE 8000

# Optional: Run tests automatically inside the container (uncomment if needed)
# RUN pip install pytest
# RUN pytest app/tests/

# Start FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
