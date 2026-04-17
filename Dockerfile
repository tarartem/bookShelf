# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend and frontend code to the container
COPY backend/ ./backend/
COPY frontend/ ./frontend/


# Setup data storage
RUN mkdir -p uploads/books uploads/covers data
VOLUME [ "/app/uploads", "/app/data" ]

# Expose port
EXPOSE 8000

# Start FastAPI application
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
