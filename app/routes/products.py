from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from app.models.product import Product, ProductCreate
from app.auth.auth_settings import require_roles

router = APIRouter()

# Aquí simulamos la "base de datos" de productos
# Ahora almacenamos instancias del modelo Product
products_db: List[Product] = [
    Product(id=1, nombre="Martillo", descripcion="Martillo de carpintero con mango de madera.", precio=7500, stock=120, marca="MarcaX", codigo="MTR001", isPromo=False, isNew=True, modelo="MC-100"),
    Product(id=2, nombre="Taladro Eléctrico", descripcion="Potente taladro percutor de 800W.", precio=45200, stock=45, marca="PowerDrill", codigo="TAL045", isPromo=True, isNew=False, modelo="TP-800"),
    Product(id=3, nombre="Lijadora", descripcion="Lijadora orbital para acabados finos.", precio=22000, stock=60, marca="LijaPro", codigo="LIJ020", isPromo=True, isNew=True, modelo="LO-500"),
    Product(id=4, nombre="Destornillador", descripcion="Set de destornilladores de precisión.", precio=3200, stock=200, marca="DestroMax", codigo="DST100", isPromo=False, isNew=False, modelo="SET-DM")
]

# Un contador para generar IDs únicos para los nuevos productos
# Asegura que el ID sea mayor que cualquier ID existente
next_product_id = max([p.id for p in products_db]) + 1 if products_db else 1

# --- FUNCIONES AUXILIARES PARA GESTIÓN DE PRODUCTOS (ACCESIBLES DESDE OTROS MÓDULOS) ---

def get_product_by_id_from_db(product_id: int) -> Optional[Product]:
    """
    Busca y devuelve un producto por su ID desde la base de datos simulada.
    """
    for product in products_db:
        if product.id == product_id:
            return product
    return None

def update_product_stock(product_id: int, quantity_change: int) -> bool:
    """
    Actualiza el stock de un producto.
    quantity_change puede ser positivo (añadir stock) o negativo (reducir stock).
    Devuelve True si el stock se actualizó con éxito, False en caso contrario (ej. stock insuficiente).
    """
    product = get_product_by_id_from_db(product_id)
    if product:
        new_stock = product.stock + quantity_change
        if new_stock >= 0:
            product.stock = new_stock
            return True
    return False

# --- ENDPOINTS DE LA API ---

# Endpoint para obtener el catálogo de productos con filtros de promoción y novedad
@router.get("/", response_model=List[Product], summary="Obtener catálogo de productos (con filtros de promoción y novedad)")
def get_products(
    promo: Optional[bool] = Query(None, description="Filtrar sólo productos en promoción"),
    new: Optional[bool] = Query(None, description="Filtrar sólo productos nuevos")
):
    """
    Obtiene el catálogo de productos.
    - Si `promo=true`, devuelve sólo los productos con isPromo=True.
    - Si `new=true`, devuelve sólo los productos con isNew=True.
    - Si se combinan ambos, devuelve los que cumplan ambas condiciones.
    - Sin parámetros, devuelve todos los productos.
    """
    results = products_db # Ahora trabajamos directamente con la lista de objetos Product

    if promo is not None:
        results = [p for p in results if p.isPromo == promo] # Acceso a atributo .isPromo
    if new is not None:
        results = [p for p in results if p.isNew == new]     # Acceso a atributo .isNew

    return results

# Endpoint para obtener un producto por ID
@router.get("/{product_id}", response_model=Product, summary="Obtener un producto por ID")
def get_product(product_id: int):
    product = get_product_by_id_from_db(product_id) # Usamos la nueva función auxiliar
    if product:
        return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

# Endpoint para agregar un nuevo producto al catálogo
@router.post("/", response_model=Product, summary="Agregar un nuevo producto al catálogo (Requiere Mantenedor)")
def add_product(
    product_data: ProductCreate, # Espera un cuerpo de solicitud que coincida con ProductCreate
    user=Depends(require_roles(["mantenedor"])) # Solo usuarios con rol "mantenedor"
):
    global next_product_id # Para poder modificar la variable global

    # Verificar si el código del producto ya existe para evitar duplicados
    for p in products_db:
        if p.codigo == product_data.codigo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, # 409 Conflict para recursos duplicados
                detail=f"Ya existe un producto con el código '{product_data.codigo}'."
            )

    # Crear una nueva instancia de Product con el ID generado y los datos recibidos
    new_product = Product(id=next_product_id, **product_data.dict())
    
    # Añadir el nuevo producto a la lista simulada
    products_db.append(new_product)
    
    # Incrementar el contador para el próximo producto
    next_product_id += 1
    
    # Devolver el producto creado con su nuevo ID
    return new_product