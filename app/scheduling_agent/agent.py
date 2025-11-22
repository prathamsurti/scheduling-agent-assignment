from google.adk.agents.llm_agent import LlmAgent
import sys 
from pathlib import Path 

current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.scheduling_agent._llm import lite,SYSTEM_INSTRUCTION
from app.scheduling_agent.tools import list_available_doctors,check_calendar_availability,book_doctor_appointment

root_agent = LlmAgent(
    model=lite,
    name='scheduling_agent',
    description='A helpful assistant for user questions.',
    instruction=SYSTEM_INSTRUCTION,
    tools = [list_available_doctors,
             check_calendar_availability,
             book_doctor_appointment]
)
