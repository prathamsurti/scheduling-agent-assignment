import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# 1. Setup SQLite
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "appointments.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Define Models

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    location = Column(String)
    doctors = relationship("Doctor", back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    specialization = Column(String)
    consultation_fee = Column(Numeric(10, 2), nullable=False)
    availability_text = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    
    patient_name = Column(String, nullable=False)
    patient_email = Column(String)  # Ensures email is stored
    patient_phone = Column(String)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    status = Column(String, default="Confirmed")
    notes = Column(Text) # Saves the "Reason"
    gcal_event_id = Column(String)
    source_session_id = Column(String) 
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("Doctor", back_populates="appointments")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# 3. Helper to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Helper to Seed Data
def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(Doctor).first():
        print("Database already contains data. Skipping seed.")
        db.close()
        return

    print("Seeding database...")
    cardio = Department(name="Cardiology", location="Wing A, Floor 2")
    gen_med = Department(name="General Medicine", location="Wing B, Floor 1")
    db.add_all([cardio, gen_med])
    db.commit()

    doc1 = Doctor(name="Dr. Sarah Smith", specialization="Cardiologist", consultation_fee=150.00, availability_text="Mon-Fri 9am-4pm", department_id=cardio.id)
    doc2 = Doctor(name="Dr. John Doe", specialization="General Physician", consultation_fee=80.00, availability_text="Tue-Sat 10am-6pm", department_id=gen_med.id)
    db.add_all([doc1, doc2])
    db.commit()
    db.close()
    print("Database seeded successfully!")

def get_all_doctors():
    """Helper to list doctors"""
    db = SessionLocal()
    try:
        docs = db.query(Doctor).all()
        return [f"{d.name} ({d.specialization})" for d in docs]
    finally:
        db.close()

# --- UNIFIED BOOKING HELPER ---
def create_appointment_in_db(patient_name, patient_email, doctor_name, start_time, end_time, reason, gcal_id=None):
    """
    Finds doctor, saves appointment with Name, Email, Time, and Reason.
    """
    db = SessionLocal()
    try:
        doc = db.query(Doctor).filter(Doctor.name.ilike(f"%{doctor_name}%")).first()
        
        if not doc:
            return None
            
        appt = Appointment(
            doctor_id=doc.id,
            patient_name=patient_name,
            patient_email=patient_email, # Saved
            start_time=start_time,
            end_time=end_time,
            notes=reason,                # Saved
            gcal_event_id=gcal_id,
            status="Confirmed"
        )
        db.add(appt)
        db.commit()
        db.refresh(appt)
        return appt.id, doc.name
    except Exception as e:
        print(f"DB Error: {e}")
        return None
    finally:
        db.close()