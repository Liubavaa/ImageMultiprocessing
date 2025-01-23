# Image Processing FastAPI Service

This project provides a FastAPI-based web service for processing and creating collages from two images. The service uses multiprocessing to handle large image processing tasks efficiently.

---

## Features

- Processes two uploaded images concurrently.
- Creates a collage of the processed images.
- Provides health-check functionality.

---

## Getting Started

### Prerequisites

- Docker
- Python 3.9+

---

### Build the Docker Image

1. Clone the repository and navigate to the project folder:
   ```bash
   git clone https://github.com/Liubavaa/ImageMultiprocessing.git
   cd ImageMultiprocessing
   ```

2. Build the Docker image:
   ```bash
   docker build -t image-processor .
   ```

---

### Run the Container

Run the container, exposing the necessary ports and mapping the output folder:
```bash
docker run -d \
  -p 8080:8000 \
  -v $(pwd)/results:/app/results \
  --name image-processor image-processor
```

- **Port Mapping:** Exposes the container's FastAPI app on your local port (for example `8080`).
- **Volume Mapping:** Maps the container's `/app/results` directory to `./results` on your local machine for saving collages.

---

### API Endpoints

1. **Health Check**
   - URL: `http://localhost:8080/health`
   - Method: `GET`
   - Response:
     ```json
     {"status": "healthy"}
     ```

2. **Process Images**
   - URL: `http://localhost:8080/process`
   - Method: `POST`
   - Form Data:
     - `image1`: First image file.
     - `image2`: Second image file.
     - `kernel_size`: Integer (e.g., 3 or 5).
     - `segment_size`: Integer (size of segments to process).
     - `brightness_threshold`: Integer (brightness threshold for processing).
   - Response: `application/octet-stream` with collage as an image file or an error message.

   For example look into `testing.py`.

---

### Stopping the Container

To stop and remove the container:
```bash
docker stop image-processor
docker rm image-processor
```

---

## Development

### Run Locally Without Docker

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up the environment:
   ```bash
   export OUTPUT_FOLDER=results
   mkdir -p results
   ```

3. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

---
