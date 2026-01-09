"""Interview service for character assessment."""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any

from models.character import Character
from models.stats import StatType


@dataclass
class InterviewAnswer:
    """A single answer option for a question."""
    text: str
    scores: dict[str, int]
    sets_priority: Optional[str] = None  # Dimension to prioritize


@dataclass
class InterviewQuestion:
    """A question in the interview."""
    id: str
    text: str
    answers: list[InterviewAnswer]
    multiple_select: bool = False


@dataclass
class InterviewCategory:
    """A category/section of interview questions."""
    id: str
    name: str
    intro: str
    questions: list[InterviewQuestion]


@dataclass
class InterviewData:
    """Complete interview data structure."""
    categories: list[InterviewCategory]
    dimension_info: dict[str, dict]
    
    @property
    def total_questions(self) -> int:
        """Total number of questions across all categories."""
        return sum(len(cat.questions) for cat in self.categories)
    
    def get_question(self, category_idx: int, question_idx: int) -> Optional[InterviewQuestion]:
        """Get a specific question by indices."""
        if 0 <= category_idx < len(self.categories):
            cat = self.categories[category_idx]
            if 0 <= question_idx < len(cat.questions):
                return cat.questions[question_idx]
        return None
    
    def get_category(self, category_idx: int) -> Optional[InterviewCategory]:
        """Get a category by index."""
        if 0 <= category_idx < len(self.categories):
            return self.categories[category_idx]
        return None


@dataclass
class InterviewSession:
    """Tracks progress through an interview session."""
    data: InterviewData
    current_category_idx: int = 0
    current_question_idx: int = 0
    responses: dict[str, list[int]] = field(default_factory=dict)  # question_id -> selected answer indices
    accumulated_scores: dict[str, int] = field(default_factory=dict)  # "dimension.facet" -> total score
    priority_dimension: Optional[StatType] = None
    
    @property
    def current_category(self) -> Optional[InterviewCategory]:
        """Get current category."""
        return self.data.get_category(self.current_category_idx)
    
    @property
    def current_question(self) -> Optional[InterviewQuestion]:
        """Get current question."""
        return self.data.get_question(self.current_category_idx, self.current_question_idx)
    
    @property
    def is_complete(self) -> bool:
        """Check if interview is complete."""
        return self.current_category_idx >= len(self.data.categories)
    
    @property
    def progress(self) -> float:
        """Calculate progress as 0-1 float."""
        total = self.data.total_questions
        if total == 0:
            return 1.0
        
        completed = 0
        for i, cat in enumerate(self.data.categories):
            if i < self.current_category_idx:
                completed += len(cat.questions)
            elif i == self.current_category_idx:
                completed += self.current_question_idx
        
        return completed / total
    
    @property
    def questions_answered(self) -> int:
        """Number of questions answered."""
        return len(self.responses)
    
    def answer_current(self, answer_indices: list[int]) -> bool:
        """
        Record answer(s) for current question and advance.
        Returns True if interview is complete.
        """
        question = self.current_question
        if not question:
            return True
        
        # Store response
        self.responses[question.id] = answer_indices
        
        # Accumulate scores from selected answers
        for idx in answer_indices:
            if 0 <= idx < len(question.answers):
                answer = question.answers[idx]
                for key, value in answer.scores.items():
                    self.accumulated_scores[key] = self.accumulated_scores.get(key, 0) + value
                
                # Check for priority setting
                if answer.sets_priority:
                    try:
                        self.priority_dimension = StatType(answer.sets_priority)
                    except ValueError:
                        pass
        
        # Advance to next question
        return self._advance()
    
    def _advance(self) -> bool:
        """Advance to next question. Returns True if complete."""
        cat = self.current_category
        if not cat:
            return True
        
        self.current_question_idx += 1
        
        # Check if we need to move to next category
        if self.current_question_idx >= len(cat.questions):
            self.current_question_idx = 0
            self.current_category_idx += 1
        
        return self.is_complete
    
    def go_back(self) -> bool:
        """Go back to previous question. Returns False if can't go back."""
        if self.current_question_idx > 0:
            self.current_question_idx -= 1
            return True
        elif self.current_category_idx > 0:
            self.current_category_idx -= 1
            cat = self.current_category
            if cat:
                self.current_question_idx = len(cat.questions) - 1
            return True
        return False
    
    def apply_to_character(self, character: Character) -> None:
        """Apply accumulated scores to character."""
        character.apply_interview_scores(self.accumulated_scores)
        character.interview_responses = dict(self.responses)
        
        if self.priority_dimension:
            character.set_priority(self.priority_dimension)
        
        character.assessment_completed = True
        character.title = character.get_title()


class InterviewService:
    """Service for managing interview flow."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize with optional custom data path."""
        if data_path is None:
            # Default to the bundled questions file
            data_path = Path(__file__).parent.parent / "data" / "interview_questions.json"
        
        self.data_path = data_path
        self._data: Optional[InterviewData] = None
    
    def load_data(self) -> InterviewData:
        """Load and parse interview data from JSON."""
        if self._data is not None:
            return self._data
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Parse categories
        categories = []
        for cat_data in raw_data.get("categories", []):
            questions = []
            for q_data in cat_data.get("questions", []):
                answers = []
                for a_data in q_data.get("answers", []):
                    answers.append(InterviewAnswer(
                        text=a_data["text"],
                        scores=a_data.get("scores", {}),
                        sets_priority=a_data.get("sets_priority"),
                    ))
                
                questions.append(InterviewQuestion(
                    id=q_data["id"],
                    text=q_data["text"],
                    answers=answers,
                    multiple_select=q_data.get("multiple_select", False),
                ))
            
            categories.append(InterviewCategory(
                id=cat_data["id"],
                name=cat_data["name"],
                intro=cat_data["intro"],
                questions=questions,
            ))
        
        self._data = InterviewData(
            categories=categories,
            dimension_info=raw_data.get("dimensions", {}),
        )
        
        return self._data
    
    def start_session(self) -> InterviewSession:
        """Start a new interview session."""
        data = self.load_data()
        return InterviewSession(data=data)
    
    def get_dimension_info(self, dimension: str) -> dict:
        """Get info about a dimension."""
        data = self.load_data()
        return data.dimension_info.get(dimension, {})


