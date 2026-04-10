from fastapi import FastAPI
from app.routes.documents import router as document_router

app = FastAPI()

