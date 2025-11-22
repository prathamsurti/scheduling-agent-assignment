import datetime
import sys
from pathlib import Path

# --- PATH FIX ---
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# ----------------

from app.tools.calendar_client import get_calendar_service, create_event, list_upcoming_events
from app.database import create_appointment_in_db, get_all_doctors

service = get_calendar_service()

# --- TOOL 1: DISCOVERY ---
def list_available_doctors() -> str:
    """
    Returns a list of all doctors, their specializations, and consultation fees.
    Use this to help the user choose the right doctor.
    """
    try:
        doctors = get_all_doctors()
        if not doctors:
            return "System: No doctors found in database."
        return "Available Doctors:\n" + "\n".join(doctors)
    except Exception as e:
        return f"Error listing doctors: {e}"

# --- TOOL 2: CHECKING ---
def check_calendar_availability(date_str: str) -> str:
    """
    Checks availability for a specific date (YYYY-MM-DD).
    """
    try:
        events = list_upcoming_events(service, max_results=10)
        busy_times = []
        for e in events:
            start = e['start'].get('dateTime', e['start'].get('date'))
            if date_str in start:
                busy_times.append(start)
        
        if not busy_times:
            return f"The calendar is completely free on {date_str}."
        return f"Busy slots on {date_str}: {', '.join(busy_times)}"
    except Exception as e:
        return f"Error checking calendar: {e}"

# --- TOOL 3: BOOKING (Updated) ---
def book_doctor_appointment(patient_name: str, patient_email: str, doctor_name: str, date_time_iso: str, reason: str) -> str:
    """
    Books an appointment.
    YOU MUST COLLECT ALL 5 ARGUMENTS FROM THE USER BEFORE CALLING THIS.
    
    Args:
        patient_name: Full Name of the patient.
        patient_email: Email address for the calendar invite.
        doctor_name: Name of the doctor (e.g. "Dr. Sarah").
        date_time_iso: Start time in ISO format (e.g. 2025-11-22T10:00:00).
        reason: The purpose of the visit.
    """
    try:
        # 1. Calculate End Time
        start_dt = datetime.datetime.fromisoformat(date_time_iso)
        end_dt = start_dt + datetime.timedelta(hours=1)
        
        # 2. Save to Database
        # Note: We removed tool_context, so we aren't capturing session_id here anymore.
        result = create_appointment_in_db(
            patient_name=patient_name,
            patient_email=patient_email,
            doctor_name=doctor_name,
            start_time=start_dt,
            end_time=end_dt,
            reason=reason
        )
        
        if not result:
            valid_docs = list_available_doctors()
            return f"ERROR: Could not find a doctor named '{doctor_name}'. Please ask the user to pick from: {valid_docs}"
        
        appt_id, real_doc_name = result

        # 3. Save to Google Calendar
        create_event(
            service, 
            summary=f"Appt: {patient_name} ({real_doc_name})", 
            start_iso=date_time_iso, 
            end_iso=end_dt.isoformat(),
            description=f"Reason: {reason}\nDB ID: {appt_id}",
            attendee_email=patient_email
        )
        
        return f"SUCCESS. Booked {patient_name} with {real_doc_name} at {date_time_iso}."
    except Exception as e:
        return f"Failed to book: {e}"