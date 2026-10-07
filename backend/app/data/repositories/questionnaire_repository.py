"""
Questionnaire repository operating on R2 DataBundle.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.app.data.loaders import R2DataBundle


@dataclass
class Question:
    id: str
    kind: str
    text: str
    dimension: Optional[str] = None
    skill: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        return cls(
            id=str(data.get("id", "")),
            kind=str(data.get("kind", "")),
            text=str(data.get("text", "")),
            dimension=data.get("dimension"),
            skill=data.get("skill"),
            raw_data=data,
        )


class QuestionnaireRepository:
    def __init__(self, bundle: R2DataBundle):
        self._questions: List[Question] = []
        for q in sorted(bundle.questions, key=lambda x: x.get("id", "")):
            self._questions.append(Question.from_dict(q))

    def list_questions(self, kind: Optional[str] = None) -> List[Question]:
        if not kind:
            return list(self._questions)
        k_clean = kind.strip().lower()
        return [q for q in self._questions if q.kind.lower() == k_clean]
