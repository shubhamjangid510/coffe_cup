import re
import os
import io
import shutil
import boto3
import logging
import rawpy  # For RAW file handling
from typing import List
from openai import OpenAI
from pillow_heif import register_heif_opener
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, File, HTTPException, Request


from app.core.config import config
from app.core.image_processor import trim_image
from app.core.symbol_analyzer import analyze_symbols
from app.models.schemas import CoffeeCupResponse, Reading
from app.models.schemas import UploadImageResponse

# Register HEIF/AVIF support for Pillow
register_heif_opener()


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Coffee Cup Reader API")
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Define UPLOAD_DIR dynamically based on current working directory
UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")

def parse_matlab_response(response: str) -> List[Reading]:
    """Parse MATLAB-like structure into a list of Reading objects."""
    readings = []
    current_reading = {}

    # Split response into lines and process each line
    lines = response.splitlines()
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        
        # Skip empty lines or irrelevant text
        if not line or "The interpretations align" in line or line.startswith("- "):
            continue
        
        # Check if line contains a field
        if "Reading" in line and "=" in line:
            parts = line.split("=", 1)  # Split on first '=' only
            if len(parts) != 2:
                continue
            
            field_name = parts[0].strip()  # e.g., "Reading(1).Observation"
            value = parts[1].strip()      # e.g., "{'mountain'};"
            
            # Extract the value between single quotes
            if "{'" in value and "'}" in value:
                value = value.split("{'")[1].split("'}")[0]
            else:
                continue
            
            # Determine which field this is
            if ".Observation" in field_name:
                current_reading["Observation"] = value
            elif ".Location" in field_name:
                current_reading["Location"] = value
            elif ".Strength" in field_name:
                current_reading["Strength"] = value
            elif ".Meaning" in field_name:
                current_reading["Meaning"] = value
            
            # If all fields are collected, create a Reading object
            if all(k in current_reading for k in ["Observation", "Location", "Strength", "Meaning"]):
                readings.append(Reading(
                    Observation=current_reading["Observation"],
                    Location=current_reading["Location"],
                    Strength=float(current_reading["Strength"]),
                    Meaning=current_reading["Meaning"],
                    Image=""  # Default, overridden later
                ))
                current_reading = {}
    return readings

def generate_final_reading(language:str, readings: List[Reading]) -> str:
    """Generate a final coffee cup reading narrative."""
    #prompt = "Compose a detailed coffee-cup reading based on the following symbols:\n\n"
    prompt = (
    "You are a skilled Tasseography practitioner tasked with delivering a detailed coffee cup reading. "
    "The following symbols were identified from five images of coffee traces in an empty cup. "
    "Compose a narrative that weaves their meanings into a coherent story, "
    "considering their locations within each image and strengths (1-10, where higher means stronger influence). "
    "Base your interpretation on traditional Tasseography culture, addressing the querent directly (e.g., 'You are...'). "
    "Blend insights about the past, present, and future naturally as the symbols suggest. "
    "Make it vivid and engaging."
    "Do not provide any other text or markdown text, just simply provide the reading.\n\n"
    f"Your response MUST be in the {language} language."
)
    for r in readings:
        prompt +=( f"Symbol: {r.Observation}\n"
                  f"Location: {r.Location}\n"
                  f"Strength: {r.Strength}\n"
                  f"Meaning: {r.Meaning}\n\n"
        )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000
    )
    return response.choices[0].message.content

async def convert_to_png(file: UploadFile) -> io.BytesIO:
    """Convert any image format to PNG."""
    try:
        file_bytes = await file.read()

        # Handle RAW images separately
        if file.filename.lower().endswith((".raw", ".cr2", ".nef", ".orf", ".sr2")):
            with rawpy.imread(io.BytesIO(file_bytes)) as raw:
                rgb_image = raw.postprocess()
                image = Image.fromarray(rgb_image)

        else:
            image = Image.open(io.BytesIO(file_bytes))
        
        image = image.convert("RGBA")  # Ensure compatibility with PNG
        converted_image = io.BytesIO()
        image.save(converted_image, format="PNG")
        converted_image.seek(0)

        return converted_image

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid or unsupported image format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image conversion error: {str(e)}")
    
    
@app.post("/upload_image/", response_model=UploadImageResponse)
async def upload_image(request: Request,reading_id: str, position: str, file: UploadFile = File(...)):
    """
    # Image Upload
    Upload a coffee cup image for a specific position associated with a *reading_id*.

    This endpoint allows users to upload a single image corresponding to one of the five positions 
    (*left*, *right*, *up*, *down*, *top*) for a given *reading_id*.
    
    It ensures that:
    - The *reading_id* is sanitized and valid.
    - The uploaded file meets size and format constraints.
    - Existing images for the same position are deleted before saving the new one.
    - The image is converted to PNG format before storage.
    - Storage can be either local (server storage) or AWS S3, based on environment configuration.

    Args:
        
        reading_id (str): Unique identifier for the coffee cup reading.
        
        position (str): The position of the image, must be one of *left*, *right*, *up*, *down*, *top*.
        
        file (UploadFile): The image file to be uploaded.

    Returns:
        
        UploadImageResponse: A response containing the storage location, number of uploaded images, 
        and a success message.

    Raises:
        
        HTTPException 400: 
            - If *reading_id* is invalid.
            - If *position* is not one of the allowed values.
            - If the file size exceeds 10MB.
            - If the file format is unsupported.
            - If all five positions are already occupied.
        
        HTTPException 404: If storage directory does not exist (local storage).
        
        HTTPException 500: 
            - If there is an issue deleting existing files.
            - If there is a failure in image processing or conversion.
            - If an S3 operation fails (for AWS storage)."""
            
   
    # Sanitize reading_id
    if not re.match(r'^[a-zA-Z0-9_-]+$', reading_id):
        raise HTTPException(status_code=400, detail="Invalid reading_id: only alphanumeric, underscore, and hyphen allowed")

    # Limit file size (15MB)
    if file.size > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")

    # Validate and normalize position
    allowed_positions = {"left", "right", "up", "down", "top"}
    position = position.lower()
    if position not in allowed_positions:
        raise HTTPException(status_code=400, detail="Position must be one of: left, right, up, down, top")

    # Check supported file formats
    if not any(file.filename.lower().endswith(fmt) for fmt in config.SUPPORTED_IMAGE_FORMATS):
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {file.filename}")
    
    # Convert image to PNG
    try:
        image = Image.open(io.BytesIO(await file.read()))
        image = image.convert("RGBA")  # Ensure compatibility with PNG
        converted_image = io.BytesIO()
        image.save(converted_image, format="PNG")
        converted_image.seek(0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    # File details
    file_name = f"image_{position}.png"
    s3_key = f"{reading_id}/{file_name}"

    # Check storage type
    use_server_storage = os.getenv("USE_SERVER_STORAGE", "false").lower() == "true"

    if use_server_storage:
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        bucket_name = os.getenv("AWS_S3_BUCKET")
        if not bucket_name:
            raise HTTPException(status_code=500, detail="AWS_S3_BUCKET not configured")

        try:
            # List existing images for this reading_id
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{reading_id}/")
            existing_images = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].startswith(f"{reading_id}/image_")]

            # Extract unique positions
            unique_positions = {obj.split("image_")[1].split(".")[0] for obj in existing_images}
            existing_count = len(unique_positions)

            # Delete all existing files for this position
            for img_key in existing_images:
                if img_key.startswith(f"{reading_id}/image_{position}."):
                    s3_client.delete_object(Bucket=bucket_name, Key=img_key)

            # Upload converted PNG
            s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=converted_image.getvalue(), ContentType="image/png")

            # Recount unique positions
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{reading_id}/")
            updated_images = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].startswith(f"{reading_id}/image_")]
            unique_positions = {obj.split("image_")[1].split(".")[0] for obj in updated_images}
            uploaded_count = len(unique_positions)

            if existing_count >= 5 and position not in unique_positions:
                raise HTTPException(status_code=400, detail=f"All 5 positions filled for reading_id: {reading_id}")

            is_overwrite = position in unique_positions
            storage_location = f"s3://{bucket_name}/{s3_key}"

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"S3 operation failed: {str(e)}")
    else:
        reading_dir = os.path.join(UPLOAD_DIR, reading_id)
        os.makedirs(reading_dir, exist_ok=True)

        file_path = os.path.join(reading_dir, file_name)
        existing_images = [f for f in os.listdir(reading_dir) if f.startswith("image_") and f.endswith(".png")]

        # Extract unique positions
        unique_positions = {img.split("image_")[1].split(".")[0] for img in existing_images}
        existing_count = len(unique_positions)
        is_overwrite = position in unique_positions

        # Delete all existing files for this position
        for existing_file in existing_images:
            if existing_file.startswith(f"image_{position}."):
                old_file_path = os.path.join(reading_dir, existing_file)
                try:
                    os.remove(old_file_path)
                except OSError as e:
                    raise HTTPException(status_code=500, detail=f"Failed to delete old file {old_file_path}: {str(e)}")

        # Check if all positions are filled and this is a new position
        if existing_count >= 5 and not is_overwrite:
            raise HTTPException(status_code=400, detail=f"All 5 positions filled for reading_id: {reading_id}")

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(converted_image.getvalue())
        except IOError as e:
            raise HTTPException(status_code=500, detail=f"Local upload failed: {str(e)}")

        updated_images = [f for f in os.listdir(reading_dir) if f.startswith("image_") and f.endswith(".png")]
        uploaded_count = len({img.split("image_")[1].split(".")[0] for img in updated_images})
        storage_location = file_path

    return UploadImageResponse(
        reading_id=reading_id,
        file_path=storage_location,
        uploaded_count=uploaded_count,
        message=f"Image at position {position} uploaded{' (overwritten)' if is_overwrite else ''} successfully"
    )

@app.post("/analyze_coffee_cup/", response_model=CoffeeCupResponse)
async def analyze_coffee_cup(language:str, reading_id: str):
    
    """
    # Tasseography  Reading
    Analyze five coffee cup images for a given *reading_id* and return symbolic interpretations.

    This endpoint processes images from either local storage or an AWS S3 bucket, depending on the configuration.
    
    It expects exactly five images corresponding to different positions: *left*, *right*, *up*, *down*, *top*. 
    
    The images are analyzed to extract symbolic meanings, which are then compiled into a final reading.

    Args:
    
        language (str): The language in which the final reading should be generated.
        reading_id (str): A unique identifier for the coffee cup reading, used to retrieve images.

    Returns:
    
        CoffeeCupResponse: A response containing individual symbol readings from each image and a final interpretation.

    Raises:
    
        HTTPException 400: If `reading_id` is invalid or required images are missing.
        HTTPException 404: If no images are found for the given reading_id.
        HTTPException 500: If an internal processing error occurs (e.g., S3 failure, file read issues).
"""
    # Sanitize reading_id
    if not re.match(r'^[a-zA-Z0-9_-]+$', reading_id):
        raise HTTPException(status_code=400, detail="Invalid reading_id: only alphanumeric, underscore, and hyphen allowed")

    # Define required positions
    required_positions = {"left", "right", "up", "down", "top"}
    use_server_storage = os.getenv("USE_SERVER_STORAGE", "false").lower() == "true"

    if use_server_storage:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )
        bucket_name = os.getenv("AWS_S3_BUCKET")
        if not bucket_name:
            raise HTTPException(status_code=500, detail="AWS_S3_BUCKET not configured")

        try:
            # List images in S3
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f"{reading_id}/")
            if "Contents" not in response:
                raise HTTPException(status_code=404, detail=f"No images found for reading_id: {reading_id}")
            
            existing_images = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].startswith(f"{reading_id}/image_")]
            image_dict = {obj.split("image_")[1].split(".")[0]: obj for obj in existing_images}

            # Check for all 5 positions
            if set(image_dict.keys()) != required_positions:
                missing = required_positions - set(image_dict.keys())
                raise HTTPException(status_code=400, detail=f"Missing images for positions: {', '.join(missing)}")

            # Read and analyze images
            all_readings = []
            for position, s3_key in image_dict.items():
                obj = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
                image_bytes = obj["Body"].read()

                trimmed_bytes = trim_image(image_bytes)
                raw_response = analyze_symbols(trimmed_bytes)
                readings = parse_matlab_response(raw_response)
                for reading in readings:
                    reading.Image = os.path.basename(s3_key)
                all_readings.extend(readings)

        except Exception as e:
            logger.error(f"S3 analysis failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"S3 analysis failed: {str(e)}")
    else:
        reading_dir = os.path.join(UPLOAD_DIR, reading_id)
        if not os.path.exists(reading_dir):
            raise HTTPException(status_code=404, detail=f"No images found for reading_id: {reading_id}")

        existing_images = [f for f in os.listdir(reading_dir) if f.startswith("image_") and f.endswith(tuple(config.SUPPORTED_IMAGE_FORMATS))]
        image_dict = {img.split("image_")[1].split(".")[0]: img for img in existing_images}

        # Check for all 5 positions
        if set(image_dict.keys()) != required_positions:
            missing = required_positions - set(image_dict.keys())
            raise HTTPException(status_code=400, detail=f"Missing images for positions: {', '.join(missing)}")
        logger.debug(f"All the files in the dict->{image_dict}")
        # Read and analyze images
        all_readings = []
        for position, filename in image_dict.items():
            file_path = os.path.join(reading_dir, filename)
            print(f"File path->{file_path}")
            try:
                #with open(file_path, "rb") as f:
                #    image_bytes = f.read()

                trimmed_image_path = trim_image(reading_dir, filename)
                raw_response = analyze_symbols(trimmed_image_path)
                print("Raw Response->",raw_response)
                readings = parse_matlab_response(raw_response)
                #print("readings inside the loop",readings)
                for reading in readings:
                    reading.Image = filename
                all_readings.extend(readings)
            except IOError as e:
                logger.error(f"Local file read failed: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Local file read failed: {str(e)}")

    print("ALL reading",all_readings)
    # Generate final reading
    final_reading = generate_final_reading(language, all_readings)
    return CoffeeCupResponse(readings=all_readings, final_reading=final_reading)
