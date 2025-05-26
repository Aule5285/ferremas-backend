from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# Modelo para un ítem dentro de un pedido
class OrderItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="La cantidad del producto debe ser mayor a 0")
    # Podrías añadir precio_unitario: float aquí si quieres guardar el precio en el momento de la compra

# Modelo para crear un nuevo pedido (lo que el cliente enviará)
class OrderCreate(BaseModel):
    items: List[OrderItem] # Para un pedido monoproducto, esta lista tendrá un solo ítem

# Modelo para un pedido tal como se guarda o se devuelve
class Order(BaseModel):
    id: int
    user_id: str # El username del cliente que hizo el pedido
    items: List[OrderItem]
    total_amount: float
    order_date: datetime = Field(default_factory=datetime.utcnow) # Fecha y hora de creación del pedido
    status: str = "pending" # Estado del pedido (pending, completed, cancelled, etc.)