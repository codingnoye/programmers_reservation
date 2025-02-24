from fastapi import FastAPI
from app.api.user import router as user_router
from app.api.reservation import router as reservation_router

app = FastAPI()

app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(reservation_router, prefix="/api/reservation", tags=["reservation"])