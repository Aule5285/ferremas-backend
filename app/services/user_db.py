from passlib.context import CryptContext
from app.models.user import UserInDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear contraseñas en claro
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Usuarios de prueba (ya con hash)
fake_users_db: dict[str, UserInDB] = {
    "javier_thompson": UserInDB(
        username="javier_thompson",
        role="mantenedor",
        hashed_password=get_password_hash("aONF4d6aNBIxRjlgjBRRzrS")
    ),
    "ignacio_tapia": UserInDB(
        username="ignacio_tapia",
        role="client",
        hashed_password=get_password_hash("f7rWChmQS1JYfThT")
    ),
    "stripe_sa": UserInDB(
        username="stripe_sa",
        role="service_account",
        hashed_password=get_password_hash("dzkQqDL9XZH33YDzhmsf")
    ),
}
