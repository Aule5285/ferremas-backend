from pydantic import BaseModel

class Branch(BaseModel):
    id: int
    nombre: str
    direccion: str
    ciudad: str
    telefono: str | None = None
