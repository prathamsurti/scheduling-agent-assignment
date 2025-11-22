Rugas Health Assistant 🩺

An AI-powered medical receptionist agent built with the Google Agent Development Kit (ADK), FastAPI, and Grok (via OpenRouter). It acts as a smart front-desk assistant, helping patients find doctors, check real-time availability, and book appointments directly into Google Calendar via a natural conversation.

🚀 Features

Conversational Booking: Natural language interface for patients to book appointments.

Real-time Availability: Checks Google Calendar for conflicts before confirming slots.

Calendar Integration: Automatically creates Google Calendar events and sends email invites to patients.

Smart Routing: Handles greetings and simple queries instantly (bypassing the LLM) for low latency.

Admin Dashboard: A dedicated panel to view booked appointments, doctor lists, and full chat logs.

Hallucination Guardrails: Strictly validates doctor names against the internal database before making recommendations.

Modern UI: Responsive, glassmorphism-style chat interface optimized for both mobile and desktop.

🛠️ Tech Stack

AI Framework: Google Agent Development Kit (ADK)

LLM: Grok-4.1 (via OpenRouter) / LiteLLM

Backend: FastAPI (Python)

Database: SQLite (SQLAlchemy)

Integrations: Google Calendar API (OAuth 2.0)

Frontend: HTML5, CSS3, Vanilla JS (Single Page Application)

📋 Prerequisites

Python 3.10+ installed.

A Google Cloud Project with the Google Calendar API enabled.

An OpenRouter API Key (for the LLM).

⚙️ Installation & Setup

1. Clone the Repository

git clone <your-repo-url>
cd scheduling-agent-assignment


2. Set up Virtual Environment

# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


4. Configuration

Environment Variables:
Create a .env file in app/scheduling_agent/ (or the root directory if configured) containing your API key:

OPENROUTER_API_KEY=sk-or-v1-your-key-here


Google Calendar Auth:

Go to the Google Cloud Console.

Create OAuth 2.0 Credentials. Important: Select "Desktop App" as the application type.

Download the JSON file, rename it to credentials.json, and place it in the root folder of the project.

5. Initialize Database

Run the initialization script to create appointments.db and seed it with dummy doctor data (Dr. Sarah Smith & Dr. John Doe).

python init_db.py


🚀 Running the Application

Start the FastAPI server from the root directory:

# Using uvicorn directly
uvicorn app.main:app --reload --port 8080

# OR using 'uv' if installed
uv run uvicorn app.main:app --reload --port 8080


Patient Chat: Open http://localhost:8080

Admin Panel: Open http://localhost:8080/admin

🧪 Usage Guide

Booking Flow Example

User: "Hi"

Agent: "Hello Sir/Mam! Welcome to Rugas Health. Can I please know your name?" (handled by local router)

User: "I am John. I have a fever."

Agent: (Checks DB) "I recommend Dr. John Doe (General Physician). Would you like to check his availability?"

User: "Yes, is tomorrow at 10am free?"

Agent: (Checks Calendar) "Yes, that slot is open. What is your email for the invite?"

User: "john@example.com"

Agent: (Books Appointment) "Confirmed! I have booked Dr. John Doe for you."

Admin Panel

Access the dashboard at /admin to:

View Total Appointments count.

See a directory of all doctors and their consultation fees.

Read Live Chat Logs to debug conversation flows.

📂 Project Structure

scheduling-agent-assignment/
├── app/
│   ├── main.py                # FastAPI Server & Router Logic
│   ├── database.py            # Database Models & Connection
│   ├── static/                # Frontend Assets
│   │   ├── index.html         # Patient Chat Interface
│   │   └── admin.html         # Admin Dashboard
│   ├── tools/                 # Infrastructure Tools
│   │   └── calendar_client.py # Google Calendar Logic
│   └── scheduling_agent/      # AI Logic
│       ├── agent.py           # Agent Definition
│       ├── _llm.py            # LLM Configuration & System Prompts
│       └── tools.py           # Agent-Facing Tools
├── appointments.db            # SQLite Database (Auto-generated)
├── credentials.json           # OAuth Credentials (User provided)
├── init_db.py                 # Database Seeding Script
└── requirements.txt           # Python Dependencies


⚠️ Troubleshooting

Error: redirect_uri_mismatch

Fix: Ensure you selected "Desktop App" (not Web App) when creating OAuth credentials in Google Cloud.

Error: Google Calendar API has not been used...

Fix: Click the link in the error message console to Enable the API for your project.

Error: Session with id ... already exists

Fix: Refresh the browser page. The client generates a new unique Session ID on reload.

📄 License

This project is for educational assignment submission.