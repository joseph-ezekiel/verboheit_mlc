"""
Utility function to serialize candidate details along with score summaries.
"""

from ..models import CandidateScore
from ..serializers import CandidateDetailSerializer


def get_candidate_with_scores(candidate):
    """
    Returns serialized candidate data including their exam scores, total score,
    and average score.

    Optimized to use `candidate.total_score` if it has been annotated.
    Falls back to manual calculation if not annotated.

    Args:
        candidate (Candidate): The candidate instance.

    Returns:
        dict: Serialized candidate data with appended scores, total_score, and average_score.
    """
    if hasattr(candidate, "total_score"):
        total = float(getattr(candidate, "total_score", 0) or 0)
        count = candidate.scores.count()
        avg = total / count if count else 0.0
    else:
        # Fallback to Python calculation
        scores = list(candidate.scores.all())
        total = sum(float(s.score) for s in scores)
        avg = total / len(scores) if scores else 0.0

    serializer = CandidateDetailSerializer(candidate)
    data = serializer.data
    data.update(
        {
            "scores": [
                {
                    "exam_id": s.exam.id,
                    "exam_title": s.exam.title,
                    "score": float(s.score),
                    "date_recorded": s.date_taken,
                    "last_updated": s.date_updated,
                    "submitted_by": s.submitted_by.id if s.submitted_by else None,
                }
                for s in candidate.scores.all().select_related("exam", "submitted_by")
            ],
            "total_score": total,
            "average_score": avg,
        }
    )
    return data
