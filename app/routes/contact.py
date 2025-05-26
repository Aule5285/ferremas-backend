from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.contact import ContactRequest, ContactMessage # Importamos los modelos de Contact
from app.models.user import UserInDB # Para el tipo del usuario autenticado
from app.auth.auth_settings import require_roles # Para la autorización
from app.routes.sellers import get_seller_by_id_from_db # Para verificar si el vendedor existe

router = APIRouter()

# Simulamos una "bandeja de entrada" para los mensajes de contacto
# En un sistema real, esto iría a una base de datos o un servicio de mensajería
contact_messages_db: List[ContactMessage] = []
next_contact_message_id = 1

@router.post("/send_message", response_model=ContactMessage, status_code=status.HTTP_201_CREATED, summary="Enviar un mensaje a un vendedor (Requiere Cliente)")
def send_message_to_seller(
    contact_data: ContactRequest,
    current_user: UserInDB = Depends(require_roles(["client"])) # Solo clientes pueden enviar mensajes
):
    global next_contact_message_id

    # 1. Verificar que el vendedor exista
    seller = get_seller_by_id_from_db(contact_data.seller_id)
    if not seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendedor con ID {contact_data.seller_id} no encontrado."
        )
    
    # 2. Crear el objeto de mensaje de contacto
    new_message = ContactMessage(
        id=next_contact_message_id,
        client_username=current_user.username, # El cliente que envía el mensaje
        seller_id=contact_data.seller_id,
        message=contact_data.message,
        status="sent" # Estado inicial del mensaje
    )

    # 3. Añadir el mensaje a nuestra "base de datos" simulada
    contact_messages_db.append(new_message)
    next_contact_message_id += 1

    # En un sistema real, aquí se integraría con un sistema de notificación (email, SMS, etc.)
    # para avisarle al vendedor que tiene un nuevo mensaje.
    
    return new_message

# Opcional: Endpoint para ver los mensajes enviados (solo para fines de prueba)
@router.get("/sent_messages", response_model=List[ContactMessage], summary="Ver mensajes de contacto enviados (Requiere Admin/Service Account)")
def get_sent_contact_messages(user=Depends(require_roles(["admin", "service_account"]))):
    return contact_messages_db