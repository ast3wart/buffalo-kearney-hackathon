"""Equipment X-Ray API (shell kept from Afterlife). Endpoints get added as the MVP is built."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Equipment X-Ray API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])


class Health(BaseModel):
    ok: bool


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(ok=True)
