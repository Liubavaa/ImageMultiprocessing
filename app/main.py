from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse
import uvicorn
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from PIL import Image
import cv2
import numpy as np
import io
import os
import datetime
from typing import List


multiprocessing.set_start_method('fork')

output_folder = os.getenv("OUTPUT_FOLDER", "results")
os.makedirs(output_folder, exist_ok=True)


app = FastAPI()
logger = logging.getLogger('uvicorn.error')


# Worker function to process a segment
def process_segment(image, x, y, segment_width, segment_height, threshold):
    segment = image[y:y + segment_height, x:x + segment_width]
    avg_brightness = np.mean(segment)
    if avg_brightness > threshold:
        cv2.rectangle(image, (x, y), (x + segment_width, y + segment_height), (255, 0, 0), 2)


def process_image(image: np.array, kernel_size: int, segment_size: int, brightness_threshold: int):
    logger.debug('Start processing')

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)

    # Multiprocess segments
    height, width = blurred.shape
    marked_image = cv2.cvtColor(blurred, cv2.COLOR_GRAY2RGB)

    tasks = []
    threads = multiprocessing.cpu_count()  # optimal number considering preceding multiprocessing
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for y in range(0, height, segment_size):
            for x in range(0, width, segment_size):
                segment_width = min(segment_size, width - x)
                segment_height = min(segment_size, height - y)
                tasks.append(
                    executor.submit(
                        process_segment, marked_image, x, y, segment_width, segment_height, brightness_threshold
                    )
                )
        for task in tasks:
            task.result()

    logger.debug('Done processing')
    return marked_image


def create_collage(processed_images: List[np.ndarray]):
    image1, image2 = processed_images

    # Define target dimensions based on the smaller dimensions of the two images
    target_height = min(image1.shape[0], image2.shape[0])
    target_width = min(image1.shape[1], image2.shape[1])

    processed_image1_resized = cv2.resize(image1, (target_width, target_height))
    processed_image2_resized = cv2.resize(image2, (target_width, target_height))

    collage = np.hstack([processed_image1_resized, processed_image2_resized])
    return collage


@app.post("/process")
async def process(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    kernel_size: int = Form(...),
    segment_size: int = Form(...),
    brightness_threshold: int = Form(...)):

    # Omitted as I'm not sure if client should state content_type
    # if not image1.content_type.startswith("image") or not image2.content_type.startswith("image"):
    #     raise HTTPException(status_code=400, detail="Files must be of type image.")

    # Images reading is done before multiprocessing as big images can cause errors
    try:
        image1 = Image.open(image1.file)
        image1 = np.array(image1)
        image2 = Image.open(image2.file)
        image2 = np.array(image2)
    except Exception:
        raise HTTPException(status_code=400, detail="Files must be of type image.")

    try:
        # Process images concurrently
        with ProcessPoolExecutor() as executor:
            processed_images = list(executor.map(
                process_image,
                [image1, image2],
                [kernel_size, kernel_size],
                [segment_size, segment_size],
                [brightness_threshold, brightness_threshold],
            ))
        logger.debug('Images processed')

        # Combine into collage
        collage = create_collage(processed_images)
        logger.debug('Collage created')

        # Save collage
        output_path = os.path.join(output_folder, f"final_collage_{datetime.datetime.now().strftime("%I:%M")}.png")
        Image.fromarray(collage).save(output_path)
        logger.debug('Image saved')

        # Return image as a response
        buffer = io.BytesIO()
        Image.fromarray(collage).save(buffer, format="PNG")
        buffer.seek(0)
        logger.debug('Response image created')

        return StreamingResponse(buffer, media_type="application/octet-stream") #"image/png"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")

@app.get("/health")
async def health():
    return JSONResponse(content={"status": "healthy"})

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
