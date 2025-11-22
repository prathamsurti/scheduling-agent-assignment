from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)  # e.g., "Cardiology"
    location = Column(String)              # e.g., "Floor 2, Wing A"
    
    # Relationship
    doctors = relationship("Doctor", back_populates="department")

class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)   # e.g., "Dr. Sarah Smith"
    specialization = Column(String)         # e.g., "Cardiologist"
    
    # Consultation Fee 
    consultation_fee = Column(Numeric(10, 2), nullable=False)  # e.g., 150.00
    
    # Simple availability text for the Agent to read
    availability_text = Column(String)      # e.g., "Mon-Fri 9am-5pm"
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Link to the Doctor
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    
    #patient_data 
    patient_name = Column(String, nullable=False)
    patient_phone = Column(String)
    patient_email = Column(String)
    
    # Scheduling Info
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Status & Admin Info
    status = Column(String, default="Confirmed") # Confirmed, Cancelled, Completed
    gcal_event_id = Column(String)               # To link with Google Calendar
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Optional: Link this appointment to the chat session that created it
    source_session_id = Column(String) 

    doctor = relationship("Doctor", back_populates="appointments")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # The Session ID from our Agent (e.g., "sess-12345")
    # This is how we group messages together.
    session_id = Column(String, index=True, nullable=False)
    
    # Who sent the message? ("user" or "model")
    role = Column(String, nullable=False)
    
    # The actual text content
    content = Column(Text, nullable=False)
    
    # Timestamp for ordering
    timestamp = Column(DateTime, default=datetime.utcnow)