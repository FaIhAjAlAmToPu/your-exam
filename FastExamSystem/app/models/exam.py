from typing import Optional, List, Dict

from pydantic import BaseModel
from sqlmodel import SQLModel, Field, ForeignKey, Column, JSON

# Response models with concise docstrings and field descriptions
class Question(BaseModel):
    """A single exam question."""
    question_no: int = Field(ge=1, description="Sequential question number (1, 2, ...)")
    question_text: str = Field(..., description="Text of the exam question")
    marks: float = Field(gt=0, description="Marks assigned to the question")

class Questions(BaseModel):
    """List of exam questions."""
    questions: List[Question] = Field(..., description="Collection of questions for the exam")

class Submission(BaseModel):
    """A single student submission for a question."""
    question: Question = Field(..., description="The exam question being answered")
    answer: str = Field(..., description="Student's answer to the question")

class Submissions(BaseModel):
    """List of student submissions."""
    submissions: List[Submission] = Field(..., description="Collection of submissions for the exam")

class EvaluationResult(BaseModel):
    """Evaluation result for a single question."""
    question_no: int = Field(ge=1, description="Question number being evaluated")
    marks_obtained: int = Field(ge=0, description="Marks awarded for the answer")
    feedback: str = Field(..., description="Feedback on the answer")

class EvaluationResults(BaseModel):
    """Evaluation results for all submissions."""
    evaluations: List[EvaluationResult] = Field(..., description="List of evaluations for each submission")
    penalty: float = Field(ge=0, description="Penalty applied (e.g., for late submission)")
    bonus: float = Field(ge=0, description="Bonus marks awarded (if any)")
    final_feedback: str = Field(..., description="Overall feedback for the exam")

class UserQuestions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(ForeignKey('user.id'))
    questions: dict = Field(sa_column=Column(JSON))

class UserSubmissions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(ForeignKey('user.id'))
    submissions: dict = Field(sa_column=Column(JSON))

class UserEvaluationResults(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(ForeignKey('user.id'))
    evaluation_results: dict = Field(sa_column=Column(JSON))
