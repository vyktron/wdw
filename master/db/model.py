from datetime import datetime
from pydantic import BaseModel

class DatabaseModel(BaseModel):
    id: int
    nom: str
    latitude: float
    longitude: float
    timestamp: datetime