import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """
    Authenticates with Google and returns the Calendar API service.
    Handles the 'credentials.json' -> 'token.json' flow automatically.
    """
    creds = None
    
    # 1. Look for the ROOT folder (where main.py or init_db.py are run from)
    # We assume this file is in app/tools/calendar_client.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
    
    token_path = os.path.join(root_dir, 'token.json')
    creds_path = os.path.join(root_dir, 'credentials.json')

    # 2. Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # 3. Refresh or Login if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # If refresh fails, delete token and re-login
                os.remove(token_path)
                return get_calendar_service()
        else:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"Could not find credentials.json at {creds_path}. Please download it from Google Cloud Console.")
                
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            # This will open a browser window on the server machine
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def list_upcoming_events(service, max_results=10):
    """Lists the next few events from the primary calendar."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=now,
        maxResults=max_results, 
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])

def create_event(service, summary, start_iso, end_iso, description=None, attendee_email=None):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_iso, # Format: '2025-11-23T15:00:00'
            'timeZone': 'Asia/Kolkata', 
        },
        'end': {
            'dateTime': end_iso,
            'timeZone': 'Asia/Kolkata', 
        },
    }


    # 2. Add Attendee Logic
    if attendee_email:
        event['attendees'] = [{'email': attendee_email}]

    event = service.events().insert(calendarId='primary', body=event).execute()
    return event