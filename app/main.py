from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router


app = FastAPI(
    title="PaddleOCR Document Extractor",
    description=(
        "Extract text and tables from images/PDFs "
        "and export them to Excel/Word."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    router,
    prefix="/api",
)


app.mount(
    "/",
    StaticFiles(
        directory="frontend",
        html=True,
    ),
    name="frontend",
)