from fastapi import FastAPI

from app.db import Base
from app.db import engine

from app.routes.items import router as items_router

from app.routes.ws import router as ws_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ETL API"
)

app.include_router(items_router)

app.include_router(ws_router)
