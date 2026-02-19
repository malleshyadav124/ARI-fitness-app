import json
from typing import Optional

from sqlalchemy.orm import Session

from backend.models import HealthAssessment
from backend.models.schemas import HealthAssessmentCreate


def create_health_assessment(
    db: Session, payload: HealthAssessmentCreate, summary: Optional[str] = None
) -> HealthAssessment:
    assessment = HealthAssessment(
        user_id=payload.user_id,
        responses_json=json.dumps(
            {"answers": payload.answers, "metadata": payload.metadata or {}}
        ),
        summary=summary,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


def get_latest_assessment(db: Session, user_id: int) -> Optional[HealthAssessment]:
    return (
        db.query(HealthAssessment)
        .filter(HealthAssessment.user_id == user_id)
        .order_by(HealthAssessment.created_at.desc())
        .first()
    )

