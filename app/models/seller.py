from pydantic import BaseModel

class Seller(BaseModel):
    id: int
    nombre: str
    branch_id: int
    email: str | None = None
    telefono: str | None = None
