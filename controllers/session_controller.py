import uuid
from typing import Optional, List
from db.mongo_client import sessions_collection
from models.session_models import StepResponse, Domain

async def handle_start_session(student_id: str, language: str, tier: str):
    session_id = str(uuid.uuid4())
    session_doc = {
        "session_id": session_id,
        "student_id": student_id,
        "language": language,
        "tier": tier,
        "current_step": 0,
        "history": [],
    }
    await sessions_collection.insert_one(session_doc)
    return {
        "session_id": session_id,
        "message": f"Session started for student {student_id}",
    }

async def handle_step(session_id: str, input_text: str):
    session = await sessions_collection.find_one({"session_id": session_id})
    if not session:
        raise Exception("Session not found")

    current_step = session.get("current_step", 0) + 1
    # Dummy prompt and matching_domains logic for demo
    prompt = f"Step {current_step} prompt for input: {input_text}"
    matching_domains: List[Domain] = [
        Domain(title="Data Science", description="Career in data science"),
        Domain(title="AI & ML", description="Career in Artificial Intelligence and Machine Learning"),
    ]

    # Update session with new step info
    session_update = {
        "current_step": current_step,
        "history": session.get("history", []) + [{"step": current_step, "input": input_text}]
    }
    await sessions_collection.update_one({"session_id": session_id}, {"$set": session_update})

    return StepResponse(
        prompt=prompt,
        matching_domains=matching_domains,
        message=f"Processed step {current_step}",
        step=current_step
    )