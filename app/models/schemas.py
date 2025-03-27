from pydantic import BaseModel
from typing import List

class UploadImageResponse(BaseModel):
    reading_id: str
    file_path: str
    uploaded_count: int
    message: str

class Reading(BaseModel):
    Observation: str
    Location: str
    Strength: float
    Meaning: str
    Image: str = None

class CoffeeCupResponse(BaseModel):
    readings: List[Reading]
    final_reading: str