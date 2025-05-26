import os
import requests
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class CurrencyConverter:
    def __init__(self):
        self.api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not self.api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY no encontrada en las variables de entorno.")
        # Usamos la base de USD, ya que es común y la API lo permite
        self.base_url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"

    def get_exchange_rates(self):
        """
        Obtiene las últimas tasas de cambio desde la API externa, con USD como base.
        """
        try:
            response = requests.get(self.base_url)
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            data = response.json()
            
            if data and data.get("result") == "success":
                return data["conversion_rates"]
            else:
                print(f"Error al obtener tasas de cambio: {data.get('error-type', 'Error desconocido')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión o HTTP al obtener tasas de cambio: {e}")
            return None
        except ValueError as e:
            print(f"Error al parsear JSON: {e}")
            return None

    def convert(self, amount: float, from_currency: str, to_currency: str):
        """
        Convierte una cantidad de una moneda a otra.
        Soporta USD, CLP y otras monedas que la API provea.
        """
        rates = self.get_exchange_rates()
        if not rates:
            return None # No se pudieron obtener las tasas

        # Asegurarse de que las monedas estén en mayúsculas para coincidir con la API
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in rates:
            raise ValueError(f"Moneda de origen '{from_currency}' no soportada por la API.")
        if to_currency not in rates:
            raise ValueError(f"Moneda de destino '{to_currency}' no soportada por la API.")

        # La API nos da tasas de USD a otras monedas.
        # Por lo tanto, si la moneda de origen no es USD, primero convertimos a USD.
        # Luego, convertimos de USD a la moneda de destino.

        # Paso 1: Convertir de from_currency a USD
        amount_in_usd = amount / rates[from_currency]

        # Paso 2: Convertir de USD a to_currency
        converted_amount = amount_in_usd * rates[to_currency]

        return round(converted_amount, 2) # Redondear a 2 decimales para divisas

# Para probar el servicio directamente (opcional, puedes borrar esto después)
if __name__ == "__main__":
    converter = CurrencyConverter()
    
    # Prueba obtener todas las tasas
    print("Tasas de cambio (base USD):")
    rates = converter.get_exchange_rates()
    if rates:
        print(rates.get("CLP"))
        print(rates.get("EUR"))

    # Prueba de conversión
    print("\nPruebas de conversión:")
    try:
        # Convertir 100 USD a CLP
        clp_amount = converter.convert(100, "USD", "CLP")
        if clp_amount is not None:
            print(f"100 USD a CLP: {clp_amount}")
        
        # Convertir 50000 CLP a USD
        usd_amount = converter.convert(50000, "CLP", "USD")
        if usd_amount is not None:
            print(f"50000 CLP a USD: {usd_amount}")

        # Prueba con moneda no soportada
        # converter.convert(100, "XYZ", "CLP") # Esto debería lanzar un ValueError
    except ValueError as e:
        print(f"Error en la conversión: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")