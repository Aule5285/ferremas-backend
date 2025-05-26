from fastapi import APIRouter, HTTPException, status # Añadido status
from typing import List, Optional # Añadido List, Optional
from app.models.seller import Seller # Importa el modelo Seller

router = APIRouter()

# Datos de prueba
# Ahora almacenamos instancias del modelo Seller
_sellers: List[Seller] = [
    Seller(id=1, nombre="Carlos Pérez", branch_id=1, email="carlos@ferremas.cl", telefono="9123-4567"),
    Seller(id=2, nombre="María López", branch_id=1, email="maria@ferremas.cl", telefono="9234-5678"),
    Seller(id=3, nombre="Ana Ruiz", branch_id=2, email="ana@ferremas.cl", telefono="9345-6789"),
]

# --- FUNCIONES AUXILIARES PARA GESTIÓN DE VENDEDORES (ACCESIBLES DESDE OTROS MÓDULOS) ---

def get_seller_by_id_from_db(seller_id: int) -> Optional[Seller]:
    """
    Busca y devuelve un vendedor por su ID desde la base de datos simulada.
    """
    for seller in _sellers:
        if seller.id == seller_id: # Acceso a atributo .id del modelo Pydantic
            return seller
    return None

# --- ENDPOINTS DE LA API ---

@router.get("/branches/{branch_id}/sellers", response_model=List[Seller], summary="Lista vendedores de una sucursal dada")
def get_sellers_by_branch(branch_id: int):
    """Lista vendedores de una sucursal dada."""
    # Ahora trabajamos directamente con la lista de objetos Seller
    sellers = [s for s in _sellers if s.branch_id == branch_id] # Acceso a atributo .branch_id
    return sellers

@router.get("/sellers/{seller_id}", response_model=Seller, summary="Devuelve un vendedor por su ID")
def get_seller(seller_id: int):
    """Devuelve un vendedor por su ID."""
    seller = get_seller_by_id_from_db(seller_id) # Usamos la nueva función auxiliar
    if seller:
        return seller
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendedor no encontrado") # Usando status de FastAPI