import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SUPPORTED_IMAGE_FORMATS = [
    ".jpeg", ".jpg",  # Standard compressed formats
    ".png",  # Lossless format with transparency
    ".webp",  # Modern web format, better compression than JPEG/PNG
    ".heic", ".heif",  # High-Efficiency Image Format (used by iPhones)
    ".avif",  # AV1-based format, better than HEIC and WEBP
    ".bmp",  # Uncompressed format (rarely used now)
    ".tiff", ".tif",  # High-quality lossless format used in photography
    ".gif",  # Supports animations, but only 256 colors
    ".ico",  # Icon format (used for favicons)
    ".svg",  # Vector format (used for web icons and logos),
    ".raw", # Raw Formats 
    ".cr2", 
    ".nef", 
    ".orf", 
    ".sr2"
    ]
config = Config()