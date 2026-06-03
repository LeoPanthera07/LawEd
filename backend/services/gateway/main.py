import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="LawEdAI Gateway Service",
    description="Central API Gateway dispatcing routing across auth, RAG, and courtroom services."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "auth": "http://localhost:8001",
    "rag": "http://localhost:8002",
    "courtroom": "http://localhost:8003"
}

client = httpx.AsyncClient()

@app.on_event("shutdown")
async def shutdown_event():
    await client.aclose()

async def proxy_request(service_name: str, path: str, request: Request) -> Response:
    """Dispatches request asynchronously to the corresponding target microservice."""
    target_url = f"{SERVICES[service_name]}{path}"
    
    # Copy headers and extract body
    headers = dict(request.headers)
    # Remove Host header to prevent routing errors in local proxies
    headers.pop("host", None)
    
    method = request.method
    content = await request.body()
    params = dict(request.query_params)

    # Handle file uploads specifically to courtroom service
    if "multipart/form-data" in headers.get("content-type", ""):
        # For multipart, let httpx format it. We pass through form elements.
        form = await request.form()
        files_data = []
        data_fields = {}
        for key, value in form.items():
            if hasattr(value, "file"): # It is a file upload
                file_bytes = await value.read()
                files_data.append(("files", (value.filename, file_bytes, value.content_type)))
            else:
                data_fields[key] = value

        # Remove Content-Type and Content-Length so httpx generates correct ones for the new boundary and body length
        headers.pop("content-type", None)
        headers.pop("content-length", None)

        # Dispatch with files
        try:
            r = await client.request(
                method, target_url, data=data_fields, files=files_data, params=params, headers=headers, timeout=60.0
            )
            return Response(content=r.content, status_code=r.status_code, headers=dict(r.headers))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Proxy error: {e}")

    try:
        r = await client.request(
            method, target_url, content=content, params=params, headers=headers, timeout=60.0
        )
        return Response(content=r.content, status_code=r.status_code, headers=dict(r.headers))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Proxy error: {e}")

# Auth Routes routing
@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def auth_proxy(path: str, request: Request):
    return await proxy_request("auth", f"/api/auth/{path}", request)

# RAG Routes routing
@app.api_route("/api/rag/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def rag_proxy(path: str, request: Request):
    return await proxy_request("rag", f"/api/rag/{path}", request)

# Courtroom / Case Routes routing
@app.api_route("/api/cases/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def courtroom_case_proxy(path: str, request: Request):
    return await proxy_request("courtroom", f"/api/cases/{path}", request)

@app.api_route("/api/cases", methods=["GET", "POST", "OPTIONS"])
async def courtroom_cases_root_proxy(request: Request):
    return await proxy_request("courtroom", "/api/cases", request)

# Serve Frontend static assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
