# 🚀 Free Deployment Guide — Routine AI (WellnessIQ)

This guide provides step-by-step instructions to deploy your **Flask + Scikit-Learn + Gemini AI + SQLite** application to free cloud hosting platforms.

---

## ⚡ Hosting Options Comparison (100% Free)

| Platform | Best For | Storage Persistence | Cold Start Delay | Custom Domain Support |
| :--- | :--- | :--- | :--- | :--- |
| **PythonAnywhere** | **SQLite DB Persistence & Zero Latency** | ✅ Permanent local disk | ⚡ None (Instant) | ❌ Free subdomain only |
| **Render.com** | **Easiest Deployment & Modern UI** | ⚠️ Ephemeral (resets on restart) | 🕒 30–50 sec spin-up | ✅ Supported |
| **Hugging Face Spaces** | **High-RAM ML Inference (16GB)** | ⚠️ Ephemeral | 🕒 20–30 sec spin-up | ❌ Hugging Face URL |
| **Koyeb** | **Global Docker Micro-VMs** | ⚠️ Ephemeral | 🕒 Fast (<15s) | ✅ Supported |

---

## 📌 STEP 0: Push Project to GitHub (Required for All Platforms)

Before deploying to Render, PythonAnywhere, or Koyeb, your project must be hosted on GitHub:

1. Open PowerShell or Command Prompt in your project directory (`c:\Users\rasto\Desktop\major`):
   ```powershell
   git init
   git add .
   git commit -m "Prepare Routine AI app for production deployment"
   ```
2. Create a **New Repository** on [GitHub](https://github.com/new) named `routine-ai`.
3. Connect and push your code:
   ```powershell
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/routine-ai.git
   git branch -M main
   git push -u origin main
   ```

---

## 🟢 OPTION 1: Deploy on Render.com (Recommended for Cloud Web Service)

Render provides free HTTPS web service hosting connected directly to GitHub.

### Step 1: Create Render Web Service
1. Sign up / Log in to [Render.com](https://render.com/).
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your GitHub account.
4. Choose your `routine-ai` repository.

### Step 2: Configure Service Settings
- **Name**: `routine-ai`
- **Region**: Oregon (US) or closest to your users
- **Branch**: `main`
- **Root Directory**: *(leave blank)*
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: **Free** ($0/month)

### Step 3: Add Environment Variables
Scroll to **Environment Variables** and add:
- `SECRET_KEY` = `a_strong_random_secret_key_123!`
- `GEMINI_API_KEY` = `your_gemini_api_key_here` (optional, fallback key is configured)

### Step 4: Deploy & Verify
1. Click **Create Web Service**.
2. Render will build the environment and run Gunicorn.
3. In ~2 minutes, your live URL will be active (e.g., `https://routine-ai.onrender.com`).

> [!NOTE]
> **Free Tier Sleep Behavior**: Render free services spin down after 15 minutes of inactivity. The first request after sleep will take 30–50 seconds to wake up the server.

---

## 🐍 OPTION 2: Deploy on PythonAnywhere (Best for Persistent SQLite Data & 0 Cold Start)

PythonAnywhere is specifically designed for Python web apps. It keeps your SQLite database (`users.db`) saved permanently on disk with **zero cold-start latency**.

### Steps:
1. Create a free account at [PythonAnywhere.com](https://www.pythonanywhere.com/).
2. Go to the **Consoles** tab and open a **Bash Console**.
3. Clone your GitHub repository:
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/routine-ai.git
   cd routine-ai
   ```
4. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. Go to the **Web** tab in PythonAnywhere:
   - Click **Add a new web app**.
   - Choose **Manual Configuration** -> **Python 3.10** (or 3.11).
   - Under **Code**:
     - **Source code path**: `/home/YOUR_USERNAME/routine-ai`
     - **Working directory**: `/home/YOUR_USERNAME/routine-ai`
   - Under **Virtualenv**:
     - Enter path: `/home/YOUR_USERNAME/routine-ai/venv`
   - Under **WSGI Configuration File**:
     - Click the link to edit the file, erase everything and paste:
       ```python
       import sys
       path = '/home/YOUR_USERNAME/routine-ai'
       if path not in sys.path:
           sys.path.append(path)

       from app import app as application
       ```
6. Click the green **Reload YOUR_USERNAME.pythonanywhere.com** button at the top.
7. Your app is live with **permanent SQLite data retention**!

---

## 🤗 OPTION 3: Deploy on Hugging Face Spaces (Best for ML Model Inference)

If your Scikit-Learn models (`model.pkl`) require dedicated CPU RAM, Hugging Face provides **16 GB RAM for free**.

### Steps:
1. Sign up at [Hugging Face](https://huggingface.co/).
2. Click your profile picture -> **New Space**.
3. Set **Space Name**: `routine-ai`
4. Select **Space SDK**: **Docker** or **Gradio/Flask** (Select Docker -> Blank).
5. Clone the space locally, add your project files + `Dockerfile`:
   ```dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 7860
   CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
   ```
6. Push to Hugging Face Git, and your app will launch!

---

## 🗄️ Database Strategy: Preserving User Data for Free

Because Render and Koyeb reset the local filesystem when restarting:
1. **For zero setup & persistent local DB**: Use **PythonAnywhere** (Option 2).
2. **For Render hosting with persistent cloud database**:
   - Use [Neon.tech](https://neon.tech/) or [Supabase.com](https://supabase.com/) free PostgreSQL database.
   - You can migrate SQLite schema to PostgreSQL easily via Python `SQLAlchemy` or `psycopg2`.

---

## 🛠️ Included Deployment Config Files

Your workspace already includes all essential deployment files:
- `requirements.txt` — Pre-configured with Flask, Pandas, Scikit-learn, Google Generative AI, Gunicorn.
- `Procfile` — Pre-configured for web worker `web: gunicorn app:app`.
- `.gitignore` — Prevents committing temporary files, bytecode, and sensitive credentials.
- `app.py` — Configured to read environment variables (`PORT`, `SECRET_KEY`, `GEMINI_API_KEY`).

---

## ✅ Post-Deployment Verification Checklist

1. **User Registration & Login**: Create a test account and log in.
2. **ML Predictions**: Test the prediction flow on dashboard (`model.pkl` loading).
3. **Gemini AI Insights**: Trigger AI analysis to verify external API communication.
4. **Admin Dashboard**: Login as admin and check user management endpoints.
