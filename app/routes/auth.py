from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.auth.auth_settings import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.user_db import fake_users_db, verify_password

router = APIRouter()

@router.post("/login", summary="Iniciar sesión y obtener token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario incorrecto")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
