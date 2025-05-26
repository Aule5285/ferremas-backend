from pydantic import BaseModel
from typing import List, Optional

# --- Modelo para los ítems que se van a comprar en Stripe Checkout ---
class CheckoutItem(BaseModel):
    # 'name' y 'price' son para que Stripe muestre la descripción del producto.
    # 'quantity' es la cantidad de ese producto.
    # 'product_id' es el ID de tu producto en tu propio sistema (para referencia interna).
    product_id: int
    name: str
    price: float # Precio por unidad
    quantity: int

# --- Modelo para la solicitud de creación de una Sesión de Checkout ---
class CreateCheckoutSessionRequest(BaseModel):
    # La lista de productos que el cliente quiere comprar.
    items: List[CheckoutItem]
    # Username del cliente que realiza la compra (para tu registro interno).
    client_username: str
    # Opcional: ID de la orden si ya la tienes creada antes de ir al pago.
    order_id: Optional[int] = None
    # Opcional: ID del branch si es relevante para el pago.
    branch_id: Optional[int] = None

# --- Modelo para representar un pago en tu base de datos simulada (opcional) ---
# Podrías usar esto para registrar los pagos en tu _payments_db
class PaymentRecord(BaseModel):
    id: int # ID interno de tu sistema
    client_username: str
    stripe_session_id: str # ID de la sesión de Stripe (checkout.session.id)
    stripe_payment_intent_id: Optional[str] = None # ID del Payment Intent (si el pago se completa)
    amount_total: float # Monto total pagado
    currency: str # Moneda (ej. USD, CLP)
    status: str # Estado del pago (ej. 'pending', 'paid', 'failed')
    created_at: str # Fecha y hora de creación de la sesión (ISO format)
    updated_at: str # Última actualización del estado
    # Opcional: Referencia a los productos comprados (IDs, nombres, etc.)
    items_snapshot: List[dict] # Un snapshot de los items al momento de la compra
    order_id: Optional[int] = None # Referencia a la orden de tu sistema