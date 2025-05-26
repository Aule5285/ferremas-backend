from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Query # <--- ¡AQUÍ! Añadir Query
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional, List, Dict, Any
import json

from app.services.stripe_service import StripeService
from app.models.payment import CreateCheckoutSessionRequest, PaymentRecord
from app.auth.auth_settings import require_roles

router = APIRouter()

# Instanciamos el servicio de Stripe.
# Esto se hace una vez al inicio de la aplicación.
try:
    stripe_service = StripeService()
except ValueError as e:
    print(f"ERROR: No se pudo inicializar StripeService: {e}")
    stripe_service = None # Para evitar que la aplicación falle si las claves no están

# Endpoint para crear una sesión de checkout de Stripe
@router.post("/create-checkout-session", summary="Crear una sesión de checkout de Stripe (Requiere Cliente)")
async def create_checkout_session(
    request_data: CreateCheckoutSessionRequest,
    user=Depends(require_roles(["client"])) # Solo clientes autenticados pueden crear sesiones de pago
):
    if not stripe_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de pago no disponible debido a configuración faltante."
        )
    
    # En un escenario real, aquí podrías:
    # 1. Crear la orden en tu DB con estado "pendiente_pago".
    # 2. Asignar un ID de orden real a `request_data.order_id` si aún no lo tiene.

    checkout_url = stripe_service.create_checkout_session(
        items=request_data.items,
        client_username=request_data.client_username,
        order_id=request_data.order_id
    )

    if checkout_url:
        return {"checkout_url": checkout_url}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No se pudo crear la sesión de checkout de Stripe."
    )

# Endpoint para manejar el éxito del pago
# Stripe redirigirá al cliente a esta URL
@router.get("/success", response_class=HTMLResponse, summary="Página de éxito de pago (Redirección de Stripe)")
async def payment_success(session_id: str = Query(...)): # <--- AQUÍ se usa Query
    # Aquí puedes recuperar información adicional de la sesión de Stripe si es necesario
    # O, más comúnmente, tu backend esperaría el webhook de Stripe para confirmar el pago.
    # Esta página es más que nada para la experiencia del usuario.

    # En un sistema real, podrías consultar el estado de la sesión si no confías solo en el webhook
    # (aunque el webhook es la forma más fiable de confirmación).
    payment_record = stripe_service.get_payment_record_by_session_id(session_id)
    
    if payment_record and payment_record.get("status") == "paid":
        return HTMLResponse(f"""
            <h1>¡Pago exitoso! 🎉</h1>
            <p>Gracias por tu compra.</p>
            <p>ID de Sesión de Stripe: {session_id}</p>
            <p>El estado del pago es: {payment_record.get('status').upper()}</p>
            <p>Un email de confirmación ha sido enviado.</p>
            <a href="/">Volver al inicio</a>
        """)
    else:
        return HTMLResponse(f"""
            <h1>Estado del pago desconocido o pendiente</h1>
            <p>Gracias por tu compra, pero el estado del pago para la sesión {session_id} aún no se ha confirmado o ha fallado.</p>
            <p>Por favor, revisa tu correo electrónico para la confirmación de la orden.</p>
            <a href="/">Volver al inicio</a>
        """, status_code=status.HTTP_202_ACCEPTED) # 202 Accepted, el pago podría estar en proceso.

# Endpoint para manejar la cancelación del pago
# Stripe redirigirá al cliente a esta URL
@router.get("/cancel", response_class=HTMLResponse, summary="Página de cancelación de pago (Redirección de Stripe)")
async def payment_cancel():
    return HTMLResponse("""
        <h1>Pago Cancelado 😔</h1>
        <p>Tu pago ha sido cancelado. Puedes intentar de nuevo.</p>
        <a href="/">Volver al inicio</a>
    """)

# Endpoint para recibir los webhooks de Stripe
# ¡IMPORTANTE! Este endpoint NO requiere autenticación porque es llamado por Stripe.
@router.post("/webhook", summary="Recibir y procesar eventos de webhook de Stripe (NO REQUIERE AUTENTICACIÓN)", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request):
    if not stripe_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de pago (webhooks) no disponible debido a configuración faltante."
        )

    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    if not sig_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falta el encabezado Stripe-Signature")

    event_data = stripe_service.handle_webhook_event(payload, sig_header)

    if event_data is None:
        # handle_webhook_event ya imprime el error, aquí solo devolvemos un estado de error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al procesar el evento de webhook o firma inválida.")

    # Si todo va bien, Stripe espera un 200 OK
    return Response(status_code=status.HTTP_200_OK, content=json.dumps({"received": True, "event_type": event_data.get('event_type')}))

# Endpoint opcional para ver los registros de pago simulados (solo para desarrollo/debugging)
@router.get("/records", summary="Obtener registros de pagos simulados (Solo para desarrollo)", response_model=List[Dict[str, Any]])
async def get_payment_records():
    if not stripe_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de pago no disponible."
        )
    return stripe_service.payment_records