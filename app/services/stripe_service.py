import os
import stripe
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import datetime

# Importamos el modelo de productos de tu aplicación para obtener el precio real
# Y la base de datos simulada de productos
from app.routes.products import products_db # ¡AJUSTADO AQUÍ! Importamos directamente products_db
from app.models.payment import CheckoutItem # Importamos el modelo de los ítems de checkout

# Cargar variables de entorno del archivo .env
load_dotenv()

class StripeService:
    def __init__(self):
        # Configurar la clave secreta de Stripe
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.success_url = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:8000/payments/success")
        self.cancel_url = os.getenv("STRIPE_CANCEL_URL", "http://localhost:8000/payments/cancel")

        if not self.secret_key or not self.webhook_secret:
            raise ValueError("Las claves STRIPE_SECRET_KEY y STRIPE_WEBHOOK_SECRET deben estar configuradas en .env")

        stripe.api_key = self.secret_key

        # Para simular una "base de datos" de registros de pago locales
        self.payment_records: List[Dict[str, Any]] = []
        self._next_payment_id = 1

    def _get_product_price_from_db(self, product_id: int) -> Optional[float]:
        """
        Función auxiliar para obtener el precio de un producto de tu base de datos simulada.
        """
        # Ahora usamos products_db directamente, que ya es una lista de objetos Product
        for product_data in products_db:
            if product_data.id == product_id:
                return product_data.price
        return None

    def create_checkout_session(self, items: List[CheckoutItem], client_username: str, order_id: Optional[int] = None) -> Optional[str]:
        """
        Crea una sesión de checkout de Stripe.
        Devuelve la URL de la sesión de checkout.
        """
        line_items = []
        total_amount = 0.0

        for item in items:
            # Obtener el precio real de tu "base de datos" de productos
            product_price = self._get_product_price_from_db(item.product_id)
            if product_price is None:
                print(f"Error: Producto con ID {item.product_id} no encontrado en la base de datos de productos.")
                return None # O lanzar una HTTPException

            # Stripe espera el precio en centavos (o la unidad más pequeña de la moneda)
            # Y debe ser un entero. Multiplicamos por 100 y convertimos a int.
            unit_amount_cents = int(product_price * 100)
            
            line_items.append({
                'price_data': {
                    'currency': 'usd', # ¡Importante! Stripe Checkout solo soporta un conjunto limitado de monedas directamente. USD es muy común.
                    'product_data': {
                        'name': item.name,
                        'metadata': { # Puedes añadir metadata a Stripe para tu referencia
                            'product_id': str(item.product_id),
                        },
                    },
                    'unit_amount': unit_amount_cents,
                },
                'quantity': item.quantity,
            })
            total_amount += (product_price * item.quantity)

        if not line_items:
            print("Error: No hay ítems válidos para crear la sesión de checkout.")
            return None

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment', # Para pagos únicos
                success_url=self.success_url + "?session_id={CHECKOUT_SESSION_ID}", # Stripe reemplaza {CHECKOUT_SESSION_ID}
                cancel_url=self.cancel_url,
                metadata={ # Puedes añadir metadata a la sesión de Stripe
                    'client_username': client_username,
                    'order_id': str(order_id) if order_id is not None else 'N/A',
                    'total_amount_clp': str(round(total_amount, 2)) # Opcional: registrar el monto original en CLP si se usó conversión
                },
                # Aquí puedes especificar un customer_email si ya lo tienes para precargar
                # customer_email='cliente@ejemplo.com',
            )
            
            # Registrar el intento de pago localmente (puedes adaptarlo a tu PaymentRecord model)
            payment_record_data = {
                "id": self._next_payment_id,
                "client_username": client_username,
                "stripe_session_id": checkout_session.id,
                "stripe_payment_intent_id": None, # Aún no disponible
                "amount_total": total_amount, # Esto es el monto en tu moneda local si no se hizo conversión antes de enviar a Stripe
                "currency": "USD", # La moneda que usó Stripe para el checkout
                "status": "pending",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "items_snapshot": [item.model_dump() for item in items], # Guarda un snapshot de los items
                "order_id": order_id,
            }
            self.payment_records.append(payment_record_data)
            self._next_payment_id += 1
            print(f"Sesión de checkout creada: {checkout_session.url}")
            return checkout_session.url

        except stripe.error.StripeError as e:
            print(f"Error al crear sesión de checkout de Stripe: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al crear sesión de checkout: {e}")
            return None

    def handle_webhook_event(self, payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
        """
        Maneja y verifica un evento de webhook de Stripe.
        """
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            print(f"Error de ValueError al procesar webhook: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            print(f"Error de SignatureVerificationError al procesar webhook: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado al verificar webhook: {e}")
            return None

        # Procesar el evento
        print(f"Webhook recibido: {event['type']}")
        
        # Aquí puedes agregar lógica para diferentes tipos de eventos
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            # print(f"Sesión de Checkout Completada: {session.id}")
            # print(session) # Descomenta para ver la sesión completa
            
            # Actualizar tu registro de pago local
            for record in self.payment_records:
                if record["stripe_session_id"] == session.id:
                    record["status"] = "paid"
                    record["stripe_payment_intent_id"] = session.payment_intent # El Payment Intent ID real
                    record["amount_total"] = session.amount_total / 100.0 # Convertir de centavos a la moneda
                    record["currency"] = session.currency.upper()
                    record["updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    print(f"Pago registrado en base de datos local para sesión {session.id}. Status: {record['status']}")
                    return record
            print(f"Advertencia: Sesión {session.id} completada, pero no encontrada en registros de pagos locales.")


        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Payment Intent Succeeded: {payment_intent.id}")
            # Lógica para manejar un pago exitoso (si no usas checkout.session.completed como principal)
            # Por ejemplo, si el pago se realizó directamente con Payment Intents API.
            # En nuestro caso, checkout.session.completed suele ser suficiente.

        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']
            print(f"Sesión de Checkout: Pago Asíncrono Exitoso: {session.id}")
            # Lógica para pagos que toman tiempo en confirmarse (ej. algunos métodos de pago)

        # Puedes añadir más tipos de eventos que te interesen:
        # elif event['type'] == 'charge.refunded':
        #     charge = event['data']['object']
        #     print(f"Reembolso de cargo: {charge.id}")

        return {"status": "success", "event_type": event['type']}

    def get_payment_record_by_session_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro de pago local por su ID de sesión de Stripe.
        """
        for record in self.payment_records:
            if record["stripe_session_id"] == session_id:
                return record
        return None