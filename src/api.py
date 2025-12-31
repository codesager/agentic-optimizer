
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph import app as workflow_app
from src.state import SMAState

app = FastAPI(title="Agentic Optimizer API", version="1.0.0")

# In-memory storage for job results (in a real app, use a DB)
jobs: Dict[str, Dict[str, Any]] = {}

class MandateRequest(BaseModel):
    mandate: str
    investment_amount: float
    thread_id: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

def run_workflow(job_id: str, mandate: str, investment_amount: float, thread_id: str):
    """
    Background task to run the LangGraph workflow.
    """
    try:
        jobs[job_id]["status"] = "running"
        
        initial_state: SMAState = {
            "user_mandate": mandate,
            "portfolio_value": investment_amount, # Pre-inject amount
            "is_interactive": False # Run in non-blocking API mode
        }
        
        config = {"recursion_limit": 50, "configurable": {"thread_id": thread_id}}
        
        # Invoke workflow
        final_state = workflow_app.invoke(initial_state, config=config)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = final_state
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        import traceback
        traceback.print_exc()

@app.post("/analyze", response_model=JobResponse)
async def analyze_portfolio(request: MandateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    thread_id = request.thread_id or job_id
    
    jobs[job_id] = {
        "status": "pending",
        "mandate": request.mandate,
        "created_at": str(uuid.uuid1())
    }
    
    background_tasks.add_task(
        run_workflow, 
        job_id, 
        request.mandate, 
        request.investment_amount,
        thread_id
    )
    
    return {
        "job_id": job_id,
        "status": "pending",
        "message": "Portfolio analysis started"
    }

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return job

from src.agents.allocation_agent import allocation_agent_node

@app.post("/jobs/{job_id}/approve")
async def approve_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job is not in a completed state to approve")
        
    current_state = job["result"]
    
    # Manually append approval feedback
    current_state.setdefault("feedback", []).append("APPROVED by User Override via Web UI")
    
    # Run allocation agent manually since the graph ended early
    try:
        print(f"Manually triggering allocation for job {job_id}")
        allocation_updates = allocation_agent_node(current_state)
        
        # Merge updates into result
        job["result"].update(allocation_updates)
        
        return {"status": "success", "message": "Portfolio approved and allocated"}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Allocation failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Agentic Optimizer API is running"}
