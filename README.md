# 🌿 MindCaps – AI-Powered Psychological Support Assistant (Backend)

A Flask REST API providing empathetic, AI-driven psychological support.
Analyzes emotional content, detects crisis situations, and generates
motivational messages. Integrated with the MindCaps React Native frontend.

## ⚙️ Tech Stack
- Python + Flask
- Mistral AI & Turkcell AI (LLM integration)
- Emotion Analysis (joy, sadness, fear, anger, disgust, surprise)
- Multilingual: Turkish & English

## 💡 Features
- AI-generated supportive responses based on user input
- Emotion analysis returned as structured JSON
- Crisis situation detection with safe guidance
- "Future self" motivational message generation

## 📡 Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | AI response to user input |
| `/analyze-emotions` | POST | Emotional content analysis |
| `/get-next-question` | GET | Next question in past sequence |
| `/get-now-question` | GET | Next question in present sequence |
| `/generate-future-message` | POST | Motivational message from future self |

## 🔗 Related
- Frontend: [MindCaps React Native App](https://github.com/Busrwa/MindCaps)

## 🚀 Getting Started
```bash
git clone https://github.com/Busrwa/Mindcaps_Backend.git
cd Mindcaps_Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
