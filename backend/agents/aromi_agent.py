from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from backend.models import ChatHistory, HealthAssessment, WorkoutPlan
from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    GeneratePlanRequest,
    HealthAssessmentCreate,
)
from backend.services.groq_client import GroqClient, try_parse_json
from backend.services.health_assessment_service import get_latest_assessment
from backend.services.nutrition_service import log_meal
from backend.services.user_service import get_or_create_demo_user

# Groq/OpenAI only accept these roles; no custom keys.
VALID_ROLES = frozenset({"system", "user", "assistant"})
GROQ_MODEL = "llama-3.1-8b-instant"


def _normalize_messages(raw: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Ensure messages follow exact OpenAI format: only role + content; no None; valid roles."""
    out: List[Dict[str, str]] = []
    for m in raw:
        if not isinstance(m, dict):
            continue
        role = (m.get("role") or "user")
        if isinstance(role, str):
            role = role.strip().lower()
        if role not in VALID_ROLES:
            role = "user"
        content = m.get("content")
        if content is None:
            content = ""
        if not isinstance(content, str):
            content = str(content)
        out.append({"role": role, "content": content})
    return out


def _ensure_system_and_user(messages: List[Dict[str, str]], default_system: str, last_user: str) -> List[Dict[str, str]]:
    """Ensure at least one system and one user message for Groq."""
    has_system = any(m.get("role") == "system" for m in messages)
    has_user = any(m.get("role") == "user" for m in messages)
    result = list(messages)
    if not has_system:
        result.insert(0, {"role": "system", "content": default_system})
    if not has_user:
        result.append({"role": "user", "content": last_user})
    return result


SYSTEM_PROMPT = """You are AROMI, an AI fitness and wellness coach for the ArogyaMitra platform.

Your job is to:
- Interpret the user's health assessment, goals, and chat messages.
- Decide when to call tools for workout planning, nutrition, or plan adjustment.
- Respond in a concise, empathetic, and encouraging tone.

You have access to the following TOOLS. When you respond, FIRST decide which single tool to call (or 'none'),
then answer the user. ALWAYS respond in strict JSON with this schema:
{
  "tool_to_call": "generate_workout_plan" | "analyze_health_assessment" | "fetch_nutrition_data" | "adjust_plan_based_on_feedback" | "none",
  "tool_arguments": { ... },   // arguments for the tool (object) or {} when none
  "assistant_reply": "string natural language reply for the user"
}

TOOLS OVERVIEW (decide based on conversation and user intent):
- generate_workout_plan: Plan a structured workout schedule for the user (per week, per day) based on goals and constraints.
- analyze_health_assessment: Summarize risks, strengths, and suggestions from the structured health assessment.
- fetch_nutrition_data: When the user describes meals or nutrition questions.
- adjust_plan_based_on_feedback: When the user gives feedback about difficulty, pain, boredom, or progress.
- none: When a simple conversational answer is enough and no tools are needed.
"""


class AromiAgent:
    def __init__(self, groq_client: Optional[GroqClient] = None):
        self.groq_client = groq_client or GroqClient()

    # ---- tool implementations ----

    def generate_workout_plan(
        self, db: Session, req: GeneratePlanRequest, user_id: int
    ) -> WorkoutPlan:
        assessment: Optional[HealthAssessment] = get_latest_assessment(db, user_id)
        context = {
            "goal": req.goal,
            "preferences": req.preferences or {},
            "assessment": json.loads(assessment.responses_json)
            if assessment is not None
            else None,
        }
        # store AI-ready context; frontend can render this JSON as a structured weekly plan
        plan = WorkoutPlan(user_id=user_id, goal=req.goal, plan_json=json.dumps(context))
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    async def analyze_health_assessment(
        self, db: Session, payload: HealthAssessmentCreate, user_id: int
    ) -> str:
        """
        Ask Groq for a concise assessment summary. Returns plain text.
        """
        user_content = json.dumps(
            {
                "user_id": user_id,
                "answers": payload.answers,
                "metadata": payload.metadata or {},
            }
        )
        raw_messages = [
            {"role": "system", "content": "You are a clinical-grade, but user-friendly, fitness and lifestyle risk assessor. Be concise."},
            {"role": "user", "content": user_content or ""},
        ]
        messages = _normalize_messages(raw_messages)
        messages = _ensure_system_and_user(
            messages,
            default_system="You are a clinical-grade, but user-friendly, fitness and lifestyle risk assessor. Be concise.",
            last_user=user_content or "No data provided.",
        )
        print("Sending to Groq (analyze_health_assessment):", messages)
        summary = await self.groq_client.chat(messages, temperature=0.2, max_tokens=300)
        return summary.strip()

    async def fetch_nutrition_data(
        self, db: Session, user_id: Optional[int], description: str
    ):
        return await log_meal(db, user_id, description)

    def adjust_plan_based_on_feedback(
        self, db: Session, user_id: int, feedback: str
    ) -> Optional[WorkoutPlan]:
        """
        Simple MVP: just attach feedback into latest plan's JSON.
        """
        latest = (
            db.query(WorkoutPlan)
            .filter(WorkoutPlan.user_id == user_id)
            .order_by(WorkoutPlan.created_at.desc())
            .first()
        )
        if not latest:
            return None

        try:
            data = json.loads(latest.plan_json)
        except Exception:
            data = {}
        history = data.get("feedback_history", [])
        history.append(feedback)
        data["feedback_history"] = history
        latest.plan_json = json.dumps(data)
        db.add(latest)
        db.commit()
        db.refresh(latest)
        return latest

    # ---- reasoning + high-level chat orchestration ----

    def _build_chat_history(
        self, db: Session, user_id: int, session_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Return chat history as list of dicts with role and content (may be normalized later)."""
        q = db.query(ChatHistory).filter(ChatHistory.user_id == user_id)
        if session_id:
            q = q.filter(ChatHistory.session_id == session_id)
        q = q.order_by(ChatHistory.created_at.asc()).limit(15)
        records = q.all()
        messages: List[Dict[str, Any]] = []
        for rec in records:
            role = rec.role if rec.role else "user"
            content = rec.message if rec.message is not None else ""
            messages.append({"role": role, "content": content})
        return messages

    def _persist_message(
        self,
        db: Session,
        *,
        user_id: int,
        session_id: Optional[str],
        role: str,
        message: str,
    ) -> None:
        record = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            message=message,
        )
        db.add(record)
        db.commit()

    async def chat(
        self, db: Session, payload: ChatRequest
    ) -> Tuple[ChatResponse, int]:
        """
        Main entry for /chat. Returns (response, resolved_user_id).
        """
        # Resolve or create user (MVP: fall back to demo user)
        user = get_or_create_demo_user(db) if payload.user_id is None else None
        user_id = user.id if user is not None else payload.user_id  # type: ignore[arg-type]

        # Persist user message
        self._persist_message(
            db,
            user_id=user_id,
            session_id=payload.session_id,
            role="user",
            message=payload.message,
        )

        history_msgs = self._build_chat_history(db, user_id, payload.session_id)
        raw_list: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT or ""},
            *history_msgs,
        ]
        messages = _normalize_messages(raw_list)
        user_content = (payload.message or "").strip() or "Hello"
        messages = _ensure_system_and_user(
            messages,
            default_system=SYSTEM_PROMPT or "You are a helpful fitness coach.",
            last_user=user_content,
        )
        # Ensure no empty messages array
        if not messages:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT or "You are a helpful fitness coach."},
                {"role": "user", "content": user_content},
            ]
        print("Sending to Groq:", messages)
        raw = await self.groq_client.chat(
            messages,
            temperature=0.7,
            max_tokens=600,
        )
        parsed = try_parse_json(raw) or {}

        tool_to_call = parsed.get("tool_to_call", "none")
        tool_args = parsed.get("tool_arguments") or {}
        assistant_reply = parsed.get("assistant_reply") or raw

        tool_used: Optional[str] = None
        tool_result: Optional[Dict[str, Any]] = None

        # tool dispatch
        try:
            if tool_to_call == "generate_workout_plan":
                req = GeneratePlanRequest(
                    user_id=user_id,
                    goal=tool_args.get("goal"),
                    preferences=tool_args.get("preferences"),
                )
                plan = self.generate_workout_plan(db, req, user_id)
                tool_used = tool_to_call
                tool_result = {
                    "plan_id": plan.id,
                    "goal": plan.goal,
                    "plan_json": json.loads(plan.plan_json),
                }
            elif tool_to_call == "analyze_health_assessment":
                latest = get_latest_assessment(db, user_id)
                if latest:
                    payload_dict = json.loads(latest.responses_json)
                    ha = HealthAssessmentCreate(
                        user_id=user_id,
                        answers=payload_dict.get("answers", []),
                        metadata=payload_dict.get("metadata", {}),
                    )
                    summary = await self.analyze_health_assessment(db, ha, user_id)
                    tool_used = tool_to_call
                    tool_result = {"summary": summary}
            elif tool_to_call == "fetch_nutrition_data":
                description = tool_args.get("description") or payload.message
                meal = await self.fetch_nutrition_data(db, user_id, description)
                tool_used = tool_to_call
                tool_result = {
                    "meal_id": meal.id,
                    "description": meal.description,
                    "calories": meal.calories,
                    "protein_g": meal.protein_g,
                    "carbs_g": meal.carbs_g,
                    "fat_g": meal.fat_g,
                }
            elif tool_to_call == "adjust_plan_based_on_feedback":
                feedback = tool_args.get("feedback") or payload.message
                updated = self.adjust_plan_based_on_feedback(db, user_id, feedback)
                if updated:
                    tool_used = tool_to_call
                    tool_result = {
                        "plan_id": updated.id,
                        "goal": updated.goal,
                        "plan_json": json.loads(updated.plan_json),
                    }
        except Exception as e:  # noqa: BLE001
            # Keep conversation going even if tool fails
            tool_used = tool_to_call
            tool_result = {"error": str(e)}

        # Persist assistant reply
        self._persist_message(
            db,
            user_id=user_id,
            session_id=payload.session_id,
            role="assistant",
            message=assistant_reply,
        )

        return (
            ChatResponse(
                reply=assistant_reply,
                tool_used=tool_used,
                tool_result=tool_result,
            ),
            user_id,
        )

