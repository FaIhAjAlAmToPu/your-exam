# Exam Generator

[This is the continuation of this small project](https://github.com/FaIhAjAlAmToPu/Gradio-MCP-Exam-System)  
A modern, secure, and AI-powered web application for creating, taking, and grading exams. Built with **FastAPI**, **Next.js**, and **LangChain**, it enables teachers to generate questions automatically, students to take exams, and automated grading with detailed feedback. Designed for self-learners.


## Features
- **User Roles**:
  - **Teachers**: Create exams, generate questions using AI, manage question banks, and review grades.
  - **Students**: Take exams, view results, and receive detailed feedback.
- **AI-Powered Question Generation**:
  - Uses **LangChain** to generate diverse, context-aware questions based on topics, difficulty, and formats (MCQ, short answer, essay).
- **Automated Grading**:
  - LangChain evaluates student answers, providing scores and qualitative feedback.
- **Exam Management**:
  - Create, edit, and delete exams.
  - Set timers, question types, and scoring rules.
- **Multi-Device Support**:
  - Users can log in from multiple devices with independent sessions.
- **Secure Authentication**:
  - JWT-based authentication with access and refresh tokens.
  - CSRF protection with per-session tokens.
  - Refresh token reuse detection to prevent unauthorized access.
- **Session Management**:
  - View and revoke active sessions (e.g., log out from a specific device).
- **Responsive UI**:
  - Modern, intuitive interface built with Next.js and Tailwind CSS.
- **Database-Driven**:
  - Stores users, exams, questions, and tokens in PostgreSQL using SQLModel.
- **Rate Limiting**:
  - Prevents brute-force attacks on authentication endpoints.

## Tech Stack
### Backend
- **FastAPI**: High-performance Python web framework for API development.
- **SQLModel**: ORM combining SQLAlchemy and Pydantic for database models.
- **PostgreSQL**: Relational database for storing users, exams, and tokens.
- **PyJWT**: JSON Web Tokens for authentication.
- **Pwdlib**: Password hashing with bcrypt.
- **SlowAPI**: Rate limiting for security.
- **LangChain**: AI-powered question generation and grading with LLM integration.

### Frontend
- **Next.js**: React framework for server-side rendering and static site generation.
- **TypeScript**: Type safety for robust frontend code.
- **Axios**: HTTP client with interceptors for token management.
- **Tailwind CSS**: Utility-first CSS for responsive design.

### AI
- **LangChain**: Framework for building applications with LLMs (e.g., question generation, grading).
- **Hugging Face Models**: Optional integration for open-source LLMs (configurable).

### Infrastructure
- **Docker**: Containerization for consistent development and deployment.
- **Nginx**: Reverse proxy for HTTPS and load balancing (production).
- **Hugging Face Spaces**: Demo deployment.

## Architecture
The Exam Generator follows a **client-server architecture** with a decoupled frontend and backend:

1. **Frontend (Next.js)**:
   - Handles user interactions (login, exam creation, taking exams).
   - Communicates with the backend via REST API.
   - Stores access and CSRF tokens in memory to prevent XSS.
   - Uses Axios interceptors for token refresh and error handling.

2. **Backend (FastAPI)**:
   - Exposes endpoints for authentication (`/auth/register`, `/login`, `/refresh`, `/logout`, `/sessions`).
   - Manages exam creation, question generation, and grading.
   - Uses SQLModel for database interactions (tables: `user`, `csrftoken`, `invalidtoken`, `exam`, `question`, `submission`).
   - Implements JWT-based authentication with refresh token rotation and reuse detection.
   - Integrates LangChain for AI-driven question generation and grading.

3. **Database (PostgreSQL)**:
   - Stores:
     - Users: `id`, `username`, `email`, `hashed_password`, `created_at`, `metadata` (JSON).
     - CSRF Tokens: `id`, `user_id`, `session_id`, `token`, `expires_at`, `metadata` (JSON).
     - Invalid Tokens: `id`, `token`, `user_id`, `session_id`, `expires_at`, `metadata` (JSON).
     - Questions: `id`, `exam_id`, `text`, `type`, `options` (JSON), `answer` (JSON).
     - Submissions: `id`, `exam_id`, `user_id`, `answers` (JSON), `grade`, `feedback` (JSON).

4. **AI Layer (LangChain)**:
   - Generates questions based on teacher input (topic, difficulty, format).
   - Grades student submissions using LLMs, providing scores and feedback.
   - Configurable to use Hugging Face models or other LLM providers.


## Authentication
- **JWT-Based**:
  - Access tokens (15-minute expiry) for API access.
  - Refresh tokens (7-day expiry) in HttpOnly cookies.
  - CSRF tokens per session to prevent cross-site attacks.
- **Reuse Detection**:
  - Invalidates all sessions if a refresh token is reused.


## LangChain Integration
- **Question Generation**:
  - Teachers input parameters (e.g., “Algebra, Medium, 10 MCQs”).
  - LangChain uses LLMs to generate questions, stored in the `question` table.
  - Example prompt: “Generate 10 algebra MCQs for high school students.”
- **Grading**:
  - Student answers are evaluated using LangChain.
  - Outputs numerical scores and feedback (e.g., “Correct, but consider simplifying the equation further”).
  - Stored in `submission` table as JSON.
- **Configuration**:
  - Uses Hugging Face models (configurable via `.env`).
  - Example: `HUGGINGFACE_API_KEY` for model access.

## Demo
Try the simplified demo on Hugging Face Spaces:  
[Exam Generator Demo](https://huggingface.co/spaces/Agents-MCP-Hackathon/Your-Exam-System)

- **Note**: The demo is hosted on Hugging Face and may have limited resources. For full functionality, deploy locally or on a cloud provider.

## Security
- **HTTPS**: Enforced with HSTS headers and Nginx (production).
- **XSS**: Access/CSRF tokens stored in memory (frontend).
- **CSRF**: Per-session tokens validated by backend middleware.
- **Reuse Detection**: Invalidates all sessions on unauthorized refresh token use.
- **Rate Limiting**: 5/minute for `/register` and `/login`, 10/hour for `/refresh`.
- **CSP**: Restricts scripts, styles, and connections to trusted sources.
- **Password Hashing**: Bcrypt and Argon2 via pwdlib.
- **Database**: No Redis; uses PostgreSQL for token storage.

## Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---