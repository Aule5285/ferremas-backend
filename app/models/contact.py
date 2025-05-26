from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Modelo para la solicitud de contacto
class ContactRequest(BaseModel):
    seller_id: int = Field(..., description="ID del vendedor al que se desea contactar")
    message: str = Field(..., min_length=10, max_length=500, description="Mensaje del cliente al vendedor")
    
# Modelo para representar una solicitud de contacto guardada/enviada
class ContactMessage(BaseModel):
    id: int
    client_username: str # El username del cliente que envió el mensaje
    seller_id: int
    message: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent" # Opcional: "read", "replied", etc.