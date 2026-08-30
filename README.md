# 🌿 Routine AI (WellnessIQ)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-000000.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-8E75B2.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **An AI-powered, multi-page personal health and wellness platform that combines classic machine learning predictive baselines with Google Gemini LLM generative coaching.**

🌐 **Live Web Application**: [routineAI.pythonanywhere.com](https://routineai.pythonanywhere.com/)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Project Structure](#-project-structure)
- [Local Setup & Quick Start](#-local-setup--quick-start)
- [Environment Variables](#-environment-variables)
- [Deployment Guide](#-deployment-guide)
- [License](#-license)

---

## 🌟 Overview

**Routine AI (WellnessIQ)** is an intelligent health management platform designed to help users establish and track daily lifestyle routines. By combining **predictive Machine Learning** (trained on physical & lifestyle metrics) with **Generative AI coaching** (powered by Google Gemini), Routine AI delivers actionable, personalized daily routines across workout, diet, mental care, and specialized hair & skin regimens.

---

## ✨ Key Features

### 🔐 1. Role-Based Authentication & Tiered Access
* **Secure Auth**: Hashed password verification via `Werkzeug.security`.
* **Automatic Admin Creation**: The first registered user automatically gains `Admin` privileges.
* **Tiered User Access**: Supports **Free** and **Premium** tiers with dynamic UI badges, tier-restricted deep-dive analytics, and upgrade modals.

### 🧠 2. Dual-Engine AI System (ML + LLM)
* **Scikit-Learn ML Core (`model.pkl`)**: Predicts clinical baseline recommendations based on user parameters (*age, weight, goal, sleep, stress, daily steps*).
* **Google Gemini LLM Integration**: Synthesizes tabular ML baselines into warm, conversational, rich-markdown daily routines.
* **Resilient Fallback**: Automatically serves baseline ML guidance if API limits or offline modes occur.

### 📊 3. Deep-Dive Routine Modules
* Customized daily and weekly breakdown tables for:
  * 🏋️ **Workout & Fitness** (Home vs. Gym options)
  * 🥗 **Nutrition & Diet** (Caloric targets & meal structures)
  * 🧘 **Mental Wellness & Mindfulness** (Stress mitigation strategies)
  * ✨ **Hair & Skin Care** (Dermatologist-aligned routines based on hydration & stress metrics)

### 📈 4. Progress Analytics & Persistence
* **Health Logging**: Automatically records every assessment in a local SQLite database (`health_logs`).
* **Progress Dashboard**: Interactive charts tracking stress trends, sleep quality, and activity levels over time.

### 🛡️ 5. Administrative Dashboard
* Live system monitoring: registered users count, total assessments, user status control (restricted/active), and platform-wide health baseline averages.

### 🌐 6. Multilingual Support (i18n)
* Instant language switching between **English** and **Hindi** (Devanagari output for Gemini AI responses).

---

## 🛠️ Architecture & Tech Stack

```
[ User Browser ] 
       │
       ▼
 [ Flask Server ] ──► [ SQLite DB (users.db) ]
       │
       ├──► [ Scikit-Learn Model (model.pkl) ]  ──► Baseline Predictions
       │
       └──► [ Google Gemini API ]              ──► Personalized AI Advice
```

* **Backend**: Python 3.10+, Flask, Gunicorn
* **ML / Data**: Scikit-Learn, Pandas, NumPy, Joblib
* **Generative AI**: `google-generativeai` (Gemini Flash)
* **Database**: SQLite3
* **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism, CSS Custom Properties), JavaScript (ES6, Service Workers, Push Notifications)

---

## 📁 Project Structure

```
major/
├── app.py                      # Main Flask app, API routes, WSGI entry
├── train_model.py              # Script to train Scikit-Learn ML models
├── evaluate_models.py         # Model performance & accuracy evaluation
├── DEPLOYMENT_GUIDE.md         # Production deployment instructions (PythonAnywhere, Render)
├── Procfile                    # Gunicorn setup for cloud deployment
├── requirements.txt            # Python dependencies
├── users.db                    # SQLite database (Users & Health Logs)
├── model.pkl                   # Trained ML model file
├── input_encoders.pkl          # Feature label encoders
├── output_encoders.pkl         # Output target label encoders
├── static/                     # CSS, JS, PWA Service Worker & icons
│   ├── index.css               # Core design tokens & styling
│   ├── notifications.js        # Browser push notification logic
│   └── sw.js                   # Service Worker for offline PWA capabilities
└── templates/                  # Jinja2 HTML templates
    ├── app_layout.html         # Main UI Shell & Sidebar
    ├── login.html              # Authentication view
    ├── admin.html              # Admin Management Dashboard
    ├── progress.html           # Progress & Analytics Dashboard
    └── views/                  # Partial components (insights, deep-dive tables)
```

---

## ⚡ Local Setup & Quick Start

### 1. Prerequisites
Ensure you have **Python 3.9+** and `git` installed.

### 2. Clone Repository & Install Dependencies
```bash
git clone https://github.com/Gravityash/routine-ai.git
cd routine-ai

# Create virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate
# Activate on Linux/macOS:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Set Environment Variables (Optional)
Create a `.env` file or export environment variables:
```bash
# Optional: Set custom Gemini API key (defaults to built-in fallback key if omitted)
export GEMINI_API_KEY="your_google_gemini_api_key"
export SECRET_KEY="your_flask_secret_key"
```

### 4. Run Application
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.

---

## ☁️ Deployment Guide

Detailed step-by-step instructions for zero-cost deployment on **PythonAnywhere**, **Render**, and **Hugging Face Spaces** are available in [`DEPLOYMENT_GUIDE.md`](./DEPLOYMENT_GUIDE.md).

### Quick PythonAnywhere WSGI Configuration
In your PythonAnywhere WSGI file (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):

```python
import sys

path = '/home/yourusername/routine-ai'
if path not in sys.path:
    sys.path.append(path)

from app import app as application  # noqa
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more details.

---

<p center="align">Crafted with ❤️ for holistic health and intelligent habit building.</p>
