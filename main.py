# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Import CORS middleware

from app.api.v1.detector_router import router as detector_router
from app.api.v1.humanize_route import router as humanize_router
from app.api.v1.paraphrase_route import router as paraphrase_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# ✅ --- CORS CONFIGURATION ---
origins = [
    "http://localhost:5174",
    "http://localhost:5173",# Vite dev server
    "http://localhost:3000", 
    "http://127.0.0.1:5173",# React dev server (CRA)
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # URLs allowed to call this API
    allow_credentials=True,       # Allow cookies / auth headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers (Content-Type, Authorization, etc.)
)
# ✅ --- END CORS CONFIG ---

# Include API routes
app.include_router(humanize_router, prefix="/api/v1")
app.include_router(paraphrase_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": f"{settings.HUMANIZER_NAME} API is running!"}

app.include_router(detector_router)
