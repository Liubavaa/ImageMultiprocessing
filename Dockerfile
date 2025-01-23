FROM python:3.9-slim

WORKDIR /app

COPY app/ /app/

# Install system dependencies required by OpenCV and other libraries
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \

RUN apt-get update
RUN pip install --no-cache-dir -r requirements.txt

ENV OUTPUT_FOLDER=/app/results
RUN mkdir -p /app/results

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
