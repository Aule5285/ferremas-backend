from pydantic import BaseModel

# Modelo base que se usa para devolver datos del usuario
class User(BaseModel):
    username: str
    role: str

# Modelo que representa un usuario guardado en base de datos (incluye contraseña hasheada)
class UserInDB(User):
    hashed_password: str
