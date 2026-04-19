🚨 Pre-Anomaly Fraud Detection System

AI-Powered Hybrid Fraud Detection (ML + GenAI + Human-in-the-loop)

📌 Overview

Traditional fraud detection systems detect fraud after it happens.
This project focuses on Pre-Anomaly Detection — identifying suspicious behavior before fraud occurs.

It combines:

🤖 Machine Learning (ML) → Pattern-based detection
🧠 Generative AI (GenAI) → Reasoning + explainability
👨‍💼 Human-in-the-loop → Manager approval workflow
🚀 Key Features
🔹 Hybrid Fraud Detection Engine
ML + GenAI combined scoring
Conflict detection → triggers investigation mode
Adaptive decision system
🔹 Explainable AI (XAI)
Human-readable fraud reasons
Auditor-friendly outputs

Example:

{
  "risk_score": 0.7,
  "decision": "HIGH RISK",
  "reasons": [
    "High transaction velocity",
    "Foreign request detected"
  ]
}
🔹 Human-in-the-Loop Workflow
Manager receives:
📧 Fraud alert email
📧 AI-generated customer email draft
Manager can:
✅ Approve → Customer notified
❌ Reject → No action
Auto-learning:
After multiple approvals → system auto-executes actions
🔹 Mule Account Detection
Detects coordinated fraud behavior:
High velocity transactions
Foreign activity patterns
Automatically flags high-risk accounts
🔹 Smart Alert System
Context-aware alerts
Suggested actions:
Freeze account
Request verification
Monitor activity
🔹 Real-Time Dashboard (Streamlit)
Live fraud monitoring
Risk score trends
Decision distribution
Account-level tracking
🔹 Transaction Simulator
Generates real-time transactions
Simulates fraud scenarios
Tests system behavior
🏗️ System Architecture
          ┌──────────────┐
          │ Simulator    │
          └──────┬───────┘
                 ↓
          ┌──────────────┐
          │ FastAPI API  │
          │ ML + GenAI   │
          └──────┬───────┘
                 ↓
      ┌──────────────┐
      │ Dashboard    │
      │ (Streamlit)  │
      └──────────────┘
                 ↓
          ┌──────────────┐
          │ Email System │
          └──────────────┘
⚙️ Tech Stack
🔹 Backend
FastAPI
Python
🔹 ML Models
XGBoost
Isolation Forest
🔹 GenAI
Groq API (LLaMA 3)
🔹 Frontend
Streamlit
Plotly
🔹 DevOps
Docker
Docker Compose
📂 Project Structure
Pre-Anomaly-Detection/
│
├── api/
│   └── app.py
│
├── src/
│   ├── models/
│   │   ├── genai_engine.py
│   │   ├── ml_model.py
│   │   └── customer_email_generator.py
│   │
│   ├── utils/
│   │   ├── alerts.py
│   │   ├── account_monitor.py
│   │   └── explainability.py
│
├── dashboard/
│   └── dashboard.py
│
├── transaction_simulator.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
🐳 Running with Docker (Recommended)
🔹 1. Add .env
GROQ_API_KEY=your_key
EMAIL_PASSWORD=your_password
EMAIL_SENDER=your_email
EMAIL_RECEIVER=manager_email
🔹 2. Run system
docker-compose up --build
🔹 3. Access
API → http://localhost:8000/docs
Dashboard → http://localhost:8501
🔁 Workflow
Transaction generated (Simulator)
Sent to API
ML + GenAI analyze
Decision Engine:
SAFE / MEDIUM / HIGH RISK
If HIGH RISK:
Email sent to Manager
Approval required
On approval:
Customer notified
Account action taken
🧠 Why Hybrid (ML + GenAI)?
Problem	ML Limitation	GenAI Advantage
Zero-day fraud	Needs training data	Detects unseen patterns
Explainability	Black-box	Human-readable
Unstructured data	Cannot process	Can analyze text/logs
Investigation	Manual	AI-assisted
Fraud rings	Hard to detect	Relationship reasoning
🔥 Future Enhancements
Kafka real-time streaming
PostgreSQL / MongoDB integration
Role-based dashboard
Risk feedback learning loop
Cloud deployment (AWS / GCP)
📸 Demo

(Add screenshots here: Dashboard, Email, API response)

👨‍💻 Author

Your Name
AI/ML Engineer

⭐ If you like this project

Give it a ⭐ on GitHub!