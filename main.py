from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.products import router as products_router
from app.routes.branches import router as branches_router
from app.routes.sellers import router as sellers_router
from app.routes.auth import router as auth_router
from app.routes.orders import router as orders_router
from app.routes.contact import router as contact_router
from app.routes.currency import router as currency_router
from app.routes.payments import router as payments_router 

app = FastAPI(title="FERREMAS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FERREMAS backend funcionando 🎉"}

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(products_router, prefix="/products", tags=["Productos"])
app.include_router(branches_router, prefix="/branches", tags=["Sucursales"])
app.include_router(sellers_router, prefix="", tags=["Vendedores"])
app.include_router(orders_router, prefix="/orders", tags=["Pedidos"])
app.include_router(contact_router, prefix="/contact", tags=["Contacto"])
app.include_router(currency_router, prefix="/currency", tags=["Divisas"])
app.include_router(payments_router, prefix="/payments", tags=["Pagos"]) 