import json
from contextlib import asynccontextmanager


from .auth.models import User
from .auth.routes import router as auth_router
from .auth.security import verify_token
from .auth.utils import get_csrf_token
from .config import FRONTEND_URL, BACKEND_URL

from typing import Annotated, Optional, List

from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware

from sqlmodel import Field, Session, text, ForeignKey, select

from .models.exam import Questions
from .settings import get_session, engine, create_db_and_tables, SessionDep

from langchain_core.prompts import PromptTemplate
from langchain.chat_models import init_chat_model
from pydantic import BaseModel


ml_models = {}




@asynccontextmanager
async def lifespan(app: FastAPI):
    # create all the tables in db
    create_db_and_tables()
    # Load the ML model
    ml_models["llm"] = init_chat_model(model="mistral-large-latest", model_provider="mistralai")
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router, prefix="/auth")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers = ["Authorization", "X-CSRF-Token", "Content-Type"],
)

@app.middleware("http")
async def verify_csrf_token(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE"] and request.url.path not in ["/auth/login", "/auth/register"]:
        auth_header = request.headers.get("Authorization")
        csrf_token = request.headers.get("X-CSRF-Token")
        if not auth_header or not csrf_token:
            raise HTTPException(status_code=403, detail="Missing authentication or CSRF token")
        session = SessionDep
        try:
            token = auth_header.replace("Bearer ", "")
            payload = verify_token(token)
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=401, detail="Invalid access token")
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            stored_csrf = get_csrf_token(csrf_token, session)
            if not stored_csrf or stored_csrf.user_id != user.id:
                raise HTTPException(status_code=403, detail="Invalid or expired CSRF token")
        except Exception:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        finally:
            session.close()
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    # CSP configuration
    if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
        # Relaxed CSP for Swagger UI and ReDoc
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' https://fastapi.tiangolo.com; "
            "connect-src 'self'; "
            "font-src 'self' https://cdn.jsdelivr.net;"
        )
    else:
        # Strict CSP for other routes (e.g., frontend)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self'; "
            f"connect-src 'self' {BACKEND_URL}; "
            "font-src 'self';"
        )
    return response
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}




@app.get("/test-db", status_code=status.HTTP_200_OK)
def test_db(session: Session = Depends(get_session)):
    try:
        session.exec(text('SELECT 1'))
        return {"db_status": "connected"}
    except Exception as e:
        return {"db_status": "error", "detail": str(e)}

# Request body model with concise descriptions
class ExamRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Exam subject (e.g., Mathematics)")
    topic: str = Field(..., min_length=1, description="Exam topic (e.g., Calculus)")
    num_questions: int = Field(..., ge=1, description="Number of questions")
    marks_each: float = Field(..., gt=0, description="Marks per question")
    exam_duration: int = Field(..., gt=0, description="Exam duration in minutes")
    deadline_choice: str = Field(..., description="Submission policy (e.g., hard_deadline)")
    comment: str = Field("", description="Optional question context")



@app.post("/exam/generate", status_code=status.HTTP_200_OK, response_model=Questions)
async def generate_exam(request: ExamRequest):
    try:
        response = generate_questions(
            subject=request.subject,
            topic=request.topic,
            num_questions=request.num_questions,
            marks_per_question=request.marks_per_question,
            total_time=request.total_time,
            comment=request.comment
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")


def generate_questions(subject, topic, num_questions, marks_per_question, total_time, comment):
    # Updated LangChain prompt template for question generation
    prompt_template = PromptTemplate(
        input_variables=["subject", "topic", "num_questions", "marks_per_question", "total_time", "comment"],
        template="""
        You are an expert educational content creator tasked with generating high-quality exam questions.
        Create {num_questions} unique exam questions for the subject '{subject}' on the topic '{topic}'.
        Each question should be worth {marks_per_question} marks and designed to fit within a total exam duration of {total_time} minutes.
        Consider the following comment(if any) for context or specific instructions: '{comment}'.
        Ensure the questions are clear, concise, and appropriate for the subject and topic, with no duplicates. And strictly follow the question structure.
        """
    )

    # Format the prompt with input values
    formatted_prompt = prompt_template.format(
        subject=subject,
        topic=topic,
        num_questions=num_questions,
        marks_per_question=marks_per_question,
        total_time=total_time,
        comment=comment
    )

    # Generate questions
    model = ml_models["llm"].with_structured_output(Questions)
    response = model.invoke(formatted_prompt)

    return response