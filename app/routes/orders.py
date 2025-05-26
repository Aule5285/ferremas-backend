from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.order import Order, OrderCreate, OrderItem # Importamos los modelos de Order
from app.models.user import UserInDB # Para el tipo del usuario autenticado
from app.auth.auth_settings import require_roles # Para la autorización
from app.routes.products import get_product_by_id_from_db, update_product_stock # Para acceder a los productos y su stock

router = APIRouter()

# Simulamos una base de datos para los pedidos
orders_db: List[Order] = []
next_order_id = 1

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED, summary="Realizar un pedido (Requiere Cliente)")
def create_order(
    order_data: OrderCreate,
    current_user: UserInDB = Depends(require_roles(["client"])) # Solo clientes pueden hacer pedidos
):
    global next_order_id

    # Para el requerimiento de "pedido monoproducto", asumimos que la lista 'items' solo contendrá un elemento.
    # Si quieres implementar multiproducto más tarde, esta estructura ya lo permite.
    if not order_data.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El pedido debe contener al menos un producto.")

    total_amount = 0.0
    processed_items: List[OrderItem] = []

    for item in order_data.items:
        product = get_product_by_id_from_db(item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {item.product_id} no encontrado."
            )
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para el producto '{product.nombre}'. Stock disponible: {product.stock}"
            )
        
        # Calcular el subtotal para este ítem
        item_subtotal = product.precio * item.quantity
        total_amount += item_subtotal
        
        # Reducir el stock del producto
        if not update_product_stock(item.product_id, -item.quantity):
            # Esto debería ser manejado por la verificación de stock anterior, pero es un fallback seguro
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el stock del producto.")
            
        processed_items.append(item) # Añadimos el item procesado a la lista final

    # Crear el objeto de pedido
    new_order = Order(
        id=next_order_id,
        user_id=current_user.username, # Asignamos el username del cliente que hizo el pedido
        items=processed_items,
        total_amount=round(total_amount, 2), # Redondeamos a 2 decimales para dinero
        status="pending" # Estado inicial
    )

    # Añadir el pedido a nuestra "base de datos" simulada
    orders_db.append(new_order)
    next_order_id += 1

    return new_order