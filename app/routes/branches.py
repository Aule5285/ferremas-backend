# app/routes/branches.py
from fastapi import APIRouter, Depends, HTTPException, status # <--- ¡Asegúrate de importar HTTPException y status!
from app.models.branch import Branch
from app.auth.auth_settings import require_roles

router = APIRouter()

branches = [
    # Corregido: Usa 'nombre', 'direccion' y añade 'ciudad'
    Branch(id=1, nombre="Sucursal Centro", direccion="Av. Principal 123", ciudad="Santiago", telefono="221234567"), # <--- Añadí un teléfono de ejemplo
    Branch(id=2, nombre="Sucursal Norte", direccion="Calle Norte 456", ciudad="Santiago", telefono="229876543"), # <--- Añadí un teléfono de ejemplo
    # Puedes añadir más sucursales si quieres para probar
]

@router.get("/", summary="Obtener listado de sucursales") # <--- Cambié el summary a español
def get_all_branches(user=Depends(require_roles(["admin", "service_account"]))):
    return branches

# --- ESTE ES EL NUEVO ENDPOINT QUE DEBES AGREGAR ---
@router.get("/{branch_id}", summary="Obtener una sucursal por ID")
def get_branch_by_id(branch_id: int):
    for branch in branches:
        if branch.id == branch_id:
            return branch
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Sucursal con ID {branch_id} no encontrada."
    )