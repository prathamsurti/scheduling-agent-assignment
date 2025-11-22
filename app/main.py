import os 
import logging 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles 
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
from dotenv import load_dotenv 
from sqlalchemy.orm import Session 
from pathlib import Path
import sys 

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.database import get_db, Appointment, ChatHistory, Doctor, Department

from google.adk.runners import Runner 
from google.adk.sessions import InMemorySessionService 
from google.genai.types import Content, Part 

from app.scheduling_agent.agent import root_agent 

load_dotenv()

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
APP_NAME = "adk-scheduling_agent"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent, 
    app_name=APP_NAME, 
    session_service=session_service
)

app = FastAPI()

class ChatRequest(BaseModel): 
    session_id: str 
    text: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest): 
    try: 
        user_id = "default_user"
        user_text = request.text.strip()
        
        # --- 1. RULE-BASED CHECK (No LLM) ---
        greetings = ["hi", "hello", "hey", "start", "greetings"]
        
        if user_text.lower() in greetings:
            hardcoded_response = "Hello Sir/Mam! Welcome to Rugas Health. Can I please know your name?"
            
            db = next(get_db())
            db.add(ChatHistory(session_id=request.session_id, role="user", content=user_text))
            db.add(ChatHistory(session_id=request.session_id, role="model", content=hardcoded_response))
            db.commit()
            
            return {"response": hardcoded_response}

        # --- 2. SESSION MANAGEMENT (FIXED) ---
        # Step A: Try to GET the session first
        session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=user_id, 
            session_id=request.session_id
        )
        
        # Step B: If missing, CREATE it (Defensively)
        if session is None: 
            try:
                session = await session_service.create_session(
                    app_name=APP_NAME, 
                    user_id=user_id, 
                    session_id=request.session_id
                )
            except Exception:
                # If creation fails (e.g. race condition where it was just created), 
                # we can safely ignore it and proceed. The session exists now.
                pass
        
        # --- 3. RUN AGENT ---
        user_content = Content(role='user', parts=[Part(text=user_text)])
        final_text = ""
        
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=request.session_id, 
            new_message=user_content
        ): 
            if event.content and event.content.parts:
                for part in event.content.parts: 
                    if part.text: 
                        final_text += part.text 
        
        # --- 4. SAVE TO DB ---
        db = next(get_db())
        db.add(ChatHistory(session_id=request.session_id, role="user", content=user_text))
        db.add(ChatHistory(session_id=request.session_id, role="model", content=final_text))
        db.commit()
        
        return {"response": final_text}
        
    except Exception as e: 
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# --- DASHBOARD ENDPOINT --- 
@app.get("/api/admin/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_docs = db.query(Doctor).count()
    total_depts = db.query(Department).count()
    total_appts = db.query(Appointment).count()
    
    doctors = db.query(Doctor, Department.name).join(Department, Doctor.department_id == Department.id).all()
    
    doc_list = []
    for doc, dept_name in doctors:
        doc_list.append({
            "id": doc.id,
            "name": doc.name,
            "specialization": doc.specialization,
            "department": dept_name,
            "fee": doc.consultation_fee,
            "availability": doc.availability_text
        })
        
    return {
        "stats": {
            "doctors": total_docs,
            "departments": total_depts,
            "appointments": total_appts
        },
        "doctors": doc_list
    }

# --- ADMIN API ENDPOINTS ---
@app.get("/api/admin/appointments")
def get_all_appointments(db: Session = Depends(get_db)):
    results = db.query(Appointment, Doctor.name).join(Doctor, Appointment.doctor_id == Doctor.id).all()
    data = []
    for appt, doc_name in results:
        data.append({
            "id": appt.id,
            "patient": appt.patient_name,
            "doctor": doc_name,
            "time": appt.start_time.strftime("%Y-%m-%d %H:%M"),
            "status": appt.status,
            "session_id": appt.source_session_id
        })
    return data

@app.get("/api/admin/chat_history")
def get_chat_logs(db: Session = Depends(get_db)):
    logs = db.query(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(100).all()
    return logs

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    
    @app.get("/")
    async def read_root():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/admin")
    async def read_admin(): 
        return FileResponse(os.path.join(STATIC_DIR,"admin.html"))        
    logger.info(f"Serving Static files from {STATIC_DIR}")
else:
    logger.warning(f"Static directory not found at {STATIC_DIR}")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)