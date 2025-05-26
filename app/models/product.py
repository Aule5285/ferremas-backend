from pydantic import BaseModel
from typing import Optional

class Product(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None  # Agregado: Descripción del producto
    precio: float
    modelo: Optional[str] = None       # Agregado: Modelo del producto
    marca: Optional[str] = None
    codigo: str                        # Modificado: 'codigo' ahora es obligatorio y de tipo str
    stock: int
    isPromo: bool = False
    isNew: bool = False

# --- NUEVO MODELO PARA CREAR PRODUCTOS (usado para POST) ---
class ProductCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    modelo: Optional[str] = None
    marca: Optional[str] = None
    codigo: str                        # 'codigo' es clave para identificar el producto, así que lo mantenemos obligatorio
    stock: int = 0                     # Valor por defecto si no se especifica al crear
    isPromo: bool = False
    isNew: bool = False