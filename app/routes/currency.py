from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.services.currency_converter import CurrencyConverter # Importamos nuestro servicio
from app.auth.auth_settings import require_roles # Para autorización, si quieres proteger este endpoint

router = APIRouter()

# Instanciamos el servicio de conversión de divisas.
# Esto se hace una vez al inicio de la aplicación.
try:
    currency_converter = CurrencyConverter()
except ValueError as e:
    # Si la clave API no está configurada, la aplicación debe fallar al inicio
    # O manejarlo de forma más robusta si se quiere que la app inicie sin la funcionalidad de conversión
    print(f"ERROR: {e}")
    currency_converter = None # Para evitar errores si la clave no está presente

@router.get("/convert", summary="Convertir monto entre divisas (Requiere Cliente/Público)")
def convert_currency(
    amount: float = Query(..., gt=0, description="Monto a convertir"),
    from_currency: str = Query(..., min_length=3, max_length=3, description="Moneda de origen (ej. 'USD', 'CLP')"),
    to_currency: str = Query(..., min_length=3, max_length=3, description="Moneda de destino (ej. 'CLP', 'USD')"),
    # Puedes elegir si este endpoint requiere autenticación o es público
    # user=Depends(require_roles(["client"])) # Descomentar para proteger
):
    if not currency_converter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Servicio de conversión de divisas no disponible debido a configuración faltante."
        )

    try:
        converted_amount = currency_converter.convert(amount, from_currency, to_currency)
        
        if converted_amount is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudieron obtener las tasas de cambio o la conversión falló."
            )
        
        return {
            "amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": converted_amount
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Captura cualquier otra excepción inesperada del servicio
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error interno en la conversión: {e}")