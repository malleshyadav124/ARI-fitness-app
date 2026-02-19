# ArogyaMitra – AI Powered Fitness & Health Companion

ArogyaMitra is an Agentic AI-based personalized fitness and nutrition assistant built using FastAPI, React (Vite), SQLite, and Groq LLM.

The application analyzes user health data, generates intelligent summaries, and creates personalized workout and nutrition plans using AI.

------------------------------------------------------------

## 🚀 Features

### 🔐 Authentication
- User Registration
- Secure Login (JWT based authentication)
- OAuth2 Password Flow
- Protected Routes

### 🩺 Health Assessment Module
- 12 structured health questions
- AI-generated health risk summary
- Personalized recommendations
- Stored per user

### 🤖 AI Chat Assistant (AROMI)
- Groq LLM integration
- Context-aware health assistant
- Chat history stored per user

### 📊 Dashboard
- Latest health assessment summary
- Total workouts generated
- Total meals logged
- Total chat messages

### 🍎 Meal Analysis
- AI-powered nutritional analysis
- Personalized dietary suggestions

### 🏋️ Workout Plan Generator
- Goal-based workout plan generation
- Plans stored and retrievable

------------------------------------------------------------

## 🛠 Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Passlib (Password Hashing)
- Groq LLM API
- Uvicorn

### Frontend
- React (Vite)
- React Router DOM
- Axios

------------------------------------------------------------

## 📁 Project Structure

ArogyaMitra-Agentic-AI/

backend/
│
├── agents/
├── auth/
├── database/
├── models/
├── routers/
├── services/
└── utils/

frontend/
│
├── src/
└── vite.config.ts

main.py  
requirements.txt  
README.md  

------------------------------------------------------------

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

git clone https://github.com/malleshyadav124/ARI-fitness-app.git  
cd ARI-fitness-app  

------------------------------------------------------------

### 2️⃣ Backend Setup

Create virtual environment:

python -m venv venv  
venv\Scripts\activate  

Install dependencies:

pip install -r requirements.txt  

Create a `.env` file in the root directory:

DATABASE_URL=sqlite:///./arogyamitra.db  
JWT_SECRET=your_secret_key  
JWT_ALGORITHM=HS256  
ACCESS_TOKEN_EXPIRE_HOURS=24  
GROQ_API_KEY=your_groq_api_key  

Run backend server:

python -m uvicorn main:app --reload --port 8000  

Open API Docs:

http://127.0.0.1:8000/docs  

------------------------------------------------------------

### 3️⃣ Frontend Setup

cd frontend  

npm install  

npm run dev  

Open application:

http://localhost:5173  

------------------------------------------------------------

## 🔑 Authentication Flow

1. User registers → receives JWT token  
2. User logs in → receives JWT token  
3. Token is stored in frontend  
4. All protected APIs require:

Authorization: Bearer <access_token>

------------------------------------------------------------

## 🤖 AI Integration

The AI assistant (AROMI) uses Groq’s OpenAI-compatible API:

https://api.groq.com/openai/v1/chat/completions  

Model used:
llama-3.1-8b-instant  

------------------------------------------------------------

## 🌟 Hackathon Highlights

- Agentic AI architecture
- Secure JWT authentication
- LLM integration
- Structured health risk assessment
- Modular backend design
- Full-stack implementation

------------------------------------------------------------

## 👩‍💻 Author

Rajeshwari  
Hackathon Submission Project  

------------------------------------------------------------
