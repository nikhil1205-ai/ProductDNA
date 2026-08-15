import sys
import json
from pathlib import Path
from typing import Optional, Any, Dict

# Add Backend root directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from data_integration.collect import integration_module_function
from data_integration.schemas.input_schema import ProductInputRequest
from data_integration.schemas.response_schema import StandardProductInput, StandardErrorResponse

app = FastAPI(
    title="ProductDNA - Module 1 (Product Intake & Document Processing)",
    description="Deterministic Product Intake API converting raw product input into Standard Product Input Objects.",
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

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ProductDNA Module 1 - Product Intake & Document Processing",
        "documentation": "/docs"
    }

@app.post(
    "/api/product-input",
    response_model=StandardProductInput,
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
    Processes input through Module 1 pipeline and returns a Standard Product Input Object.
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
            explicit_type=input_type
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
