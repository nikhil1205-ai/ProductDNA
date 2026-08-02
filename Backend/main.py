import sys
from pathlib import Path

# Add Backend root directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_integration.api.product_input import router as product_input_router

app = FastAPI(
    title="ProductDNA - Module 1 (Product Intake & Document Processing)",
    description="Deterministic Product Intake API converting arbitrary input formats into Standard Product Input Objects.",
    version="1.0.0"
)

# Enable CORS for local frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(product_input_router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ProductDNA Module 1 - Product Intake & Document Processing",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
