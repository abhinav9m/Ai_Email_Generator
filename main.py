import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

from database import init_db, save_email, get_history, toggle_favorite, delete_email, clear_all_history
from services.email_service import generate_email, refine_email, normalize_recipient, GEMINI_API_KEY

app = FastAPI(
    title="AI Email Generator",
    description="Generative AI powered email generation app using FastAPI & Gemini API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Pydantic Request Models
class GenerateRequest(BaseModel):
    purpose: str
    recipient: Optional[str] = ""
    tone: str = "Professional"
    length: Optional[str] = "Medium"
    user_message: str
    sender_name: Optional[str] = ""
    api_key: Optional[str] = None
    version: Optional[int] = 1

class RefineRequest(BaseModel):
    subject: str
    greeting: str
    body: str
    closing: str
    action: str  # 'shorter', 'formal', 'friendlier', 'grammar', 'custom'
    custom_instruction: Optional[str] = None
    api_key: Optional[str] = None
    purpose: Optional[str] = "Refinement"
    recipient: Optional[str] = ""
    sender_name: Optional[str] = ""
    user_message: Optional[str] = ""
    tone: Optional[str] = "Refined"
    length: Optional[str] = "Refined"

# API Endpoints
@app.get("/api/health")
def health_check():
    has_key = bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 5)
    return {
        "status": "healthy",
        "api_key_configured": has_key,
        "database": "connected"
    }

@app.post("/api/generate")
async def generate_email_endpoint(req: GenerateRequest):
    if not req.purpose or not req.purpose.strip():
        raise HTTPException(status_code=400, detail="Email category/purpose must be selected.")

    if not req.user_message or not req.user_message.strip() or len(req.user_message.strip()) < 3:
        raise HTTPException(status_code=400, detail="Main content and key points are required.")
        
    try:
        norm_recip = normalize_recipient(req.recipient or "")
        
        result = await generate_email(
            purpose=req.purpose,
            recipient=req.recipient or "",
            tone=req.tone,
            length=req.length or "Medium",
            user_message=req.user_message,
            sender_name=req.sender_name or "",
            custom_api_key=req.api_key
        )
        
        # Save EVERY generated email as a NEW separate history entry
        saved_record = save_email(
            purpose=req.purpose,
            recipient=norm_recip,
            tone=req.tone,
            length=req.length or "Medium",
            user_message=req.user_message,
            subject=result["subject"],
            greeting=result["greeting"],
            body=result["body"],
            closing=result["closing"],
            full_email=result["full_email"],
            user_name=req.sender_name or "",
            version=req.version or 1
        )
        
        result["id"] = saved_record.get("id")
        result["created_at"] = saved_record.get("created_at")
        result["recipient"] = norm_recip
        result["user_name"] = req.sender_name or ""
        result["version"] = saved_record.get("version", 1)
        result["purpose"] = req.purpose
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/refine")
async def refine_email_endpoint(req: RefineRequest):
    try:
        norm_recip = normalize_recipient(req.recipient or "")
        
        result = await refine_email(
            subject=req.subject,
            greeting=req.greeting,
            body=req.body,
            closing=req.closing,
            action=req.action,
            custom_instruction=req.custom_instruction,
            custom_api_key=req.api_key,
            recipient=req.recipient or "",
            sender_name=req.sender_name or ""
        )
        
        # Save refined/improved email as a NEW separate record in history
        saved_record = save_email(
            purpose=req.purpose or f"Refine ({req.action})",
            recipient=norm_recip,
            tone=req.tone or "Refined",
            length=req.length or "Refined",
            user_message=req.user_message or f"Refinement action: {req.action}",
            subject=result["subject"],
            greeting=result["greeting"],
            body=result["body"],
            closing=result["closing"],
            full_email=result["full_email"],
            user_name=req.sender_name or "",
            version=2
        )
        
        result["id"] = saved_record.get("id")
        result["created_at"] = saved_record.get("created_at")
        result["recipient"] = norm_recip
        result["user_name"] = req.sender_name or ""
        result["purpose"] = req.purpose or f"Refine ({req.action})"
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
def get_history_endpoint():
    try:
        history = get_history(limit=100)
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history/{email_id}/favorite")
def favorite_endpoint(email_id: int):
    try:
        is_fav = toggle_favorite(email_id)
        return {"status": "success", "is_favorite": is_fav}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{email_id}")
def delete_history_endpoint(email_id: int):
    try:
        deleted = delete_email(email_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Email record not found")
        return {"status": "success", "deleted_id": email_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history")
def clear_history_endpoint():
    try:
        clear_all_history()
        return {"status": "success", "message": "All history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "AI Email Generator Backend is Running."}
