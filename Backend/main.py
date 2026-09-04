import sys
import json
from pathlib import Path
from typing import Optional, Any, Dict, Union

# Add Backend root directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from product_integration_module_1.collect import integration_module_function
from product_integration_module_1.schemas.input_schema import ProductInputRequest
from product_integration_module_1.schemas.response_schema import StandardProductInput, StandardBatchResponse, StandardErrorResponse

from Evidence_collection_sources_module_2.api.routes import router as module2_router
from Evidence_extraction_module_3.api.routes import router as module3_router
from LLM_Semantic_Interpretation_module_5.router import module5_router

app = FastAPI(
    title="ProductDNA — Product Intelligence Engine",
    description="Product Intake, Resolution, and Evidence Extraction APIs.",
    version="1.0.0"
)

# Include Module 2 Product Resources Router & Module 3 Evidence Extraction Router
app.include_router(module2_router)
app.include_router(module3_router)
# Include Module 5 Semantic Interpretation Router
app.include_router(module5_router)


# Enable CORS for local & production Vercel frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://product-dna-topaz.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ProductDNA Module 1 - Product Intake & Document Processing",
        "documentation": "/docs"
    }

@app.post(
    "/api/product-input",
    response_model=Union[StandardProductInput, StandardBatchResponse],
    responses={400: {"model": StandardErrorResponse}, 422: {"model": StandardErrorResponse}}
)
async def process_product_input(
    request: Request,
    file: Optional[UploadFile] = File(None),
    input_type: Optional[str] = Form(None),
    input_text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None),
    json_data: Optional[str] = Form(None)
):
    """
    Main Product Intake Endpoint. Supports both multipart/form-data (files, forms) and application/json requests.
    Processes input through Module 1 pipeline and returns a Standard Product Input Object or Batch Response.
    """
    file_bytes: Optional[bytes] = None
    filename: Optional[str] = None
    parsed_json_data: Optional[Any] = None
    target_url: Optional[str] = url
    target_input_text: Optional[str] = input_text or product_name

    # Check if request is JSON body payload
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                req_model = ProductInputRequest(**body)
                input_type = req_model.input_type or input_type
                target_input_text = req_model.input_text or req_model.product_name or target_input_text
                target_url = req_model.url or target_url
                parsed_json_data = req_model.json_data
            elif isinstance(body, list):
                parsed_json_data = body
                input_type = "JSON"
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "ERROR", "error": f"Invalid JSON payload in request body: {str(e)}"}
            )

    # If file was uploaded
    if file:
        filename = file.filename
        try:
            file_bytes = await file.read()
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "ERROR", "error": f"Failed to read uploaded file: {str(e)}"}
            )

    # Parse form json_data parameter if string
    if json_data and parsed_json_data is None:
        try:
            parsed_json_data = json.loads(json_data)
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "ERROR", "error": f"Invalid JSON syntax in form field 'json_data': {str(e)}"}
            )

    # Run Module 1 Orchestration
    try:
        result = integration_module_function(
            file_bytes=file_bytes,
            filename=filename,
            url_str=target_url,
            json_data=parsed_json_data,
            input_text=target_input_text,
            explicit_type=input_type,
            return_batch=True
        )
        return result
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "ERROR", "error": str(ve)}
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "ERROR", "error": f"Internal processing error: {str(ex)}"}
        )

# Helper function to securely resolve Module 1 product files
def resolve_module1_file(product_id: str) -> Path:
    base_dir = (Path(__file__).resolve().parent / "input_data" / "Module_1_Standard_input").resolve()
    clean_id = Path(product_id).name
    if clean_id.endswith(".json"):
        clean_id = clean_id[:-5]
    
    file_path = (base_dir / f"{clean_id}.json").resolve()
    
    if not str(file_path).startswith(str(base_dir)):
        raise HTTPException(status_code=400, detail="Invalid product ID path.")
        
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found.")
        
    return file_path

@app.get("/api/products/module1")
async def list_module1_products():
    """Returns summary listing of all standardized products in Module_1_Standard_input."""
    base_dir = Path(__file__).resolve().parent / "input_data" / "Module_1_Standard_input"
    if not base_dir.exists():
        return {"products": []}
    
    products = []
    for json_file in base_dir.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            prod_id = data.get("request_id") or json_file.stem
            identity = data.get("identity") or {}
            source_rec = data.get("source_record") or {}
            
            row_num = source_rec.get("row_number")
            if row_num is None:
                row_num = data.get("metadata", {}).get("row_number")

            products.append({
                "product_id": prod_id,
                "filename": json_file.name,
                "row_number": row_num,
                "product_name": identity.get("product_name"),
                "part_number": identity.get("part_number"),
                "sku": identity.get("sku"),
                "brand": identity.get("brand"),
                "manufacturer": identity.get("manufacturer"),
                "model": identity.get("model"),
                "status": data.get("status", "READY_FOR_RESOLUTION")
            })
        except Exception:
            continue
            
    products.sort(key=lambda x: (x["row_number"] if x["row_number"] is not None else 999999, x["product_id"]))
    return {"products": products}

@app.get("/api/products/module1/{product_id}")
async def get_module1_product(product_id: str):
    """Returns complete StandardProductInput JSON for selected product_id."""
    file_path = resolve_module1_file(product_id)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read product file: {str(e)}")

@app.get("/api/product-registry")
async def get_product_registry():
    """Returns Organization Product Registry records from CSV."""
    registry_path = Path(__file__).resolve().parent / "product_resolution_engine" / "org_data" / "product_registry.csv"
    if not registry_path.exists():
        return {"registry": []}
    
    import csv
    try:
        records = []
        with open(registry_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        return {"registry": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load product registry: {str(e)}")

@app.post("/api/products/process-selected")
async def process_selected_product(request: Request):
    """Processes only the single selected product for downstream pipeline."""
    try:
        body = await request.json()
        product_id = body.get("product_id")
        if not product_id:
            raise HTTPException(status_code=400, detail="Missing product_id in request body")
        
        file_path = resolve_module1_file(product_id)
        with open(file_path, "r", encoding="utf-8") as f:
            product_data = json.load(f)
            
        return {
            "status": "SUCCESS",
            "message": f"Successfully loaded product '{product_id}' for downstream processing.",
            "product_id": product_id,
            "product": product_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process selected product: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
