from fastapi import FastAPI, status

from app.routers import convert, currency

app = FastAPI()

app.include_router(currency.router)
app.include_router(convert.router)
