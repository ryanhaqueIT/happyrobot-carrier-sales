from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routes import loads, carrier, negotiation, webhook, metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Acme Logistics - Carrier Sales API",
    description="Backend for HappyRobot inbound carrier sales voice agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(loads.router)
app.include_router(carrier.router)
app.include_router(negotiation.router)
app.include_router(webhook.router)
app.include_router(metrics.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
