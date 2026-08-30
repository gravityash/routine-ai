# ==========================================
# ROUTINE AI - SIMPLE VERSION (MORNING CODE)
# ==========================================

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pickle
import time
import os
import sqlite3
from functools import wraps
import google.generativeai as genai

def load_env_file(filepath='.env'):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception as e:
            print("Error loading .env file:", e)

load_env_file()



# ==========================================
# INIT APP
# ==========================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_change_me')
CORS(app)

# ==========================================
# DB SETUP & DECORATORS
# ==========================================
def get_db():
    conn = sqlite3.connect('users.db', timeout=30)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except sqlite3.OperationalError:
        pass
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()


    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            is_restricted INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            age INTEGER,
            gender TEXT,
            weight REAL,
            goal TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal TEXT,
            sleep_hours REAL,
            stress_level REAL,
            steps_walked INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            target REAL,
            progress REAL DEFAULT 0,
            unit TEXT,
            status TEXT DEFAULT 'active',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_type TEXT,
            filename TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            user_id INTEGER PRIMARY KEY,
            daily_reminder_time TEXT DEFAULT '08:00',
            weekly_reminder_day TEXT DEFAULT 'Sunday',
            weekly_reminder_time TEXT DEFAULT '20:00',
            enabled INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Safely add columns to health_logs if they don't exist
    columns_to_add = [
        ("weight", "REAL"),
        ("water_intake", "REAL"),
        ("screen_time", "REAL"),
        ("work_hours", "REAL"),
        ("protein_intake", "REAL"),
        ("calories_intake", "REAL"),
        ("exercise_minutes", "REAL"),
        ("meditation_minutes", "REAL"),
        ("gender", "TEXT")
    ]
    
    c.execute("PRAGMA table_info(health_logs)")
    existing_cols = [col[1] for col in c.fetchall()]
    
    for col_name, col_type in columns_to_add:
        if col_name not in existing_cols:
            try:
                c.execute(f"ALTER TABLE health_logs ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass
                
    # Add new user columns if they don't exist
    c.execute("PRAGMA table_info(users)")
    existing_user_cols = [col[1] for col in c.fetchall()]
    if "is_restricted" not in existing_user_cols:
        try: c.execute("ALTER TABLE users ADD COLUMN is_restricted INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass
    if "is_deleted" not in existing_user_cols:
        try: c.execute("ALTER TABLE users ADD COLUMN is_deleted INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass
    if "is_premium" not in existing_user_cols:
        try: c.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
        except sqlite3.OperationalError: pass
        
    # Mark first 50 users (ordered by ID) as premium, others as standard
    try:
        c.execute("UPDATE users SET is_premium = 1 WHERE id IN (SELECT id FROM users ORDER BY id ASC LIMIT 50)")
        c.execute("UPDATE users SET is_premium = 0 WHERE id NOT IN (SELECT id FROM users ORDER BY id ASC LIMIT 50)")
    except sqlite3.OperationalError:
        pass
                
    conn.commit()
    conn.close()


init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# AUTH & PAGES
# ==========================================
def render_view(template_name, **context):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template(template_name, **context)
    return render_template('app_layout.html', view_template=template_name, **context)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        c = conn.cursor()

        c.execute("SELECT id, password, role, is_restricted, is_deleted, is_premium FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            # Check restriction and deletion
            if user[4] == 1: # is_deleted
                flash("This account has been deleted.")
                return render_template("login.html")
            if user[3] == 1: # is_restricted
                flash("Your account has been restricted by an administrator.")
                return render_template("login.html")

            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            session['is_premium'] = user[5] if len(user) > 5 else 0
            
            # Check if user has a profile
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT * FROM user_profiles WHERE user_id=?", (user[0],))
            profile = c.fetchone()
            conn.close()
            
            if not profile:
                return redirect(url_for('onboarding'))
                
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        hashed_pw = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM users")
            count = c.fetchone()[0]
            role = 'admin' if count == 0 else 'user'
            # First 50 registered users get free premium access
            is_premium = 1 if count < 50 else 0
            
            c.execute("INSERT INTO users (username, password, role, is_premium) VALUES (?, ?, ?, ?)", (username, hashed_pw, role, is_premium))
            user_id = c.lastrowid
            conn.commit()
            conn.close()
            
            # Auto login and redirect to onboarding
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            session['is_premium'] = is_premium
            return redirect(url_for('onboarding'))
            return redirect(url_for('onboarding'))
        except sqlite3.IntegrityError:
            flash("Username already exists")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/onboarding", methods=["GET", "POST"])
@login_required
def onboarding():
    if request.method == "POST":
        age = request.form.get("age")
        gender = request.form.get("gender")
        weight = request.form.get("weight")
        goal = request.form.get("goal")
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO user_profiles (user_id, age, gender, weight, goal) VALUES (?, ?, ?, ?, ?)",
                  (session['user_id'], age, gender, weight, goal))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    return render_template("onboarding.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_view("views/dashboard.html")

@app.route("/progress")
@login_required
def progress():
    return render_view("views/progress.html")

@app.route("/ai-insights")
@login_required
def ai_insights():
    return render_view("views/ai_insights.html")

@app.route("/workout-analysis")
@app.route("/diet-analysis")
@app.route("/lifestyle-analysis")
@app.route("/mental-analysis")
@app.route("/hair-skin")
@login_required
def analytics_subpage():
    path = request.path.strip('/')
    type_map = {
        'workout-analysis': 'workout',
        'diet-analysis': 'nutrition',
        'lifestyle-analysis': 'lifestyle',
        'mental-analysis': 'mental',
        'hair-skin': 'hair_skin'
    }
    analysis_type = type_map.get(path, 'lifestyle')
    return render_view("views/analysis_partial.html", analysis_type=analysis_type)

@app.route("/goals")
@login_required
def goals():
    return render_view("views/goals.html")

@app.route("/nutrition")
@login_required
def nutrition():
    return render_view("views/analysis_partial.html", analysis_type="nutrition")

@app.route("/workout")
@login_required
def workout():
    return render_view("views/analysis_partial.html", analysis_type="workout")

@app.route("/mental-wellness")
@login_required
def mental_wellness():
    return render_view("views/analysis_partial.html", analysis_type="mental")

@app.route("/hair-skin-overview")
@login_required
def hair_skin_overview():
    return render_view("views/analysis_partial.html", analysis_type="hair_skin")

@app.route("/reports")
@login_required
def reports():
    return render_view("views/reports.html")

@app.route("/settings")
@login_required
def settings():
    return render_view("views/settings.html")

@app.route("/simple-analysis")
@login_required
def simple_analysis():
    return render_view("views/simple_analysis.html")

def get_static_simple_analysis(lang, sleep, stress, steps):
    if lang == "hindi":
        return f"""### 🩺 **आपकी सेहत का हाल (Overall Health)**
आपकी सेहत कुल मिलाकर अच्छी है! आपने रोज़ाना {int(steps)} कदम चले हैं। अच्छी जीवनशैली बनाए रखने के लिए थोड़ा और ध्यान दें।

### 🌟 **क्या बहुत अच्छा है (What is Good)**
- 👟 **कदम और एक्टिविटी:** आपने {int(steps)} कदम पूरे किए हैं जो एक बेहतरीन प्रयास है!
- 💧 **शरीर में पानी:** सही मात्रा में पानी पीना आपकी ऊर्जा बनाए रखता है।

### ⚠️ **ध्यान देने योग्य बातें (Needs Attention)**
- 🌙 **नींद का समय:** आपकी नींद अभी {sleep} घंटे है, इसे 7-8 घंटे करने की कोशिश करें।
- 🧠 **तनाव का स्तर:** आपका तनाव स्तर {stress}/10 है, थोड़ा आराम और गहरी सांसें लें।

### 🚀 **आसान 3 कदम आज ही अपनाएं (Simple 3-Step Action Plan)**
1. **रात में जल्दी सोएं:** सोने से 30 मिनट पहले फोन इस्तेमाल न करें।
2. **रोज़ 15 मिनट टहलें:** सुबह या शाम हल्की वॉक करें।
3. **पानी भरपूर पीएं:** दिनभर में कम से कम 8-10 गिलास पानी पीएं।"""
    elif lang == "hinglish":
        return f"""### 🩺 **Aapki Health Ka Haal (Overall Health)**
Aapki health overall kaafi achhi chal rahi hai! Aapne aaj lagbhag {int(steps)} steps walk kiye hain, jo ek badhiya habit hai.

### 🌟 **Kya Achha Hai (What is Good)**
- 👟 **Steps & Daily Activity:** Aapne {int(steps)} steps poore kiye hain, super work!
- 💧 **Hydration Level:** Paani achhe se peena aapko din bhar energetic rakhta hai.

### ⚠️ **Kahan Dhyan Dena Hai (Needs Attention)**
- 🌙 **Sleep Hours:** Aapki sleep abhi {sleep} hours hai, isse 7-8 hours karne ki koshish karein.
- 🧠 **Stress Level:** Aapka stress level {stress}/10 hai, thoda relax karein aur deep breathing karein.

### 🚀 **Aasaan 3 Steps Aaj Hi Karen (Simple 3-Step Action Plan)**
1. **Time pe soyein:** Sone se 30 minutes pehle mobile use band kar dein.
2. **15 Mins Walk:** Shaam ko ya subah halki walk zaroor karein.
3. **Paani khoob pijiye:** Din me kam se kam 8-10 glass paani zaroor pijiye."""
    else:
        return f"""### 🩺 **Your Health Summary**
Your health is looking great overall! You walked around {int(steps)} steps today, which is a fantastic daily effort.

### 🌟 **What is Going Great**
- 👟 **Daily Movement:** You achieved {int(steps)} steps, keeping your body active!
- 💧 **Hydration:** Drinking enough water keeps your metabolism and energy high.

### ⚠️ **What Needs a Little Care**
- 🌙 **Sleep Hours:** You got about {sleep} hours of sleep. Try aiming for 7-8 hours for full recovery.
- 🧠 **Stress Level:** Your stress is around {stress}/10. Take short relaxation breaks throughout the day.

### 🚀 **Easy 3-Step Action Plan**
1. **Sleep Early:** Turn off screens 30 minutes before bedtime.
2. **Take a Short Walk:** Enjoy a brisk 15-minute walk outside.
3. **Stay Hydrated:** Drink 8-10 glasses of fresh water daily."""


@app.route("/api/simple-analysis", methods=["POST"])
@login_required
def api_simple_analysis():
    req_data = request.json or {}
    lang = req_data.get("language", "english").lower()

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT sleep_hours, stress_level, steps_walked, water_intake, calories_intake, exercise_minutes, goal
        FROM health_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1
    """, (session['user_id'],))
    last_log = c.fetchone()
    conn.close()

    if last_log:
        sleep = last_log[0] or 6.5
        stress = last_log[1] or 5
        steps = last_log[2] or 6000
        water = last_log[3] or 2.0
        calories = last_log[4] or 2200
        exercise = last_log[5] or 20
        goal = last_log[6] or "Health Improvement"
    else:
        sleep, stress, steps, water, calories, exercise, goal = 6.5, 5, 6000, 2.0, 2200, 20, "Health Improvement"

    metrics_summary = f"Sleep: {sleep} hrs, Stress: {stress}/10, Steps: {steps}, Water: {water}L, Calories: {calories}, Exercise: {exercise} mins, Goal: {goal}"

    if lang == "hindi":
        prompt = f"""
You are a warm, friendly health coach.
Write a VERY SIMPLE, clear health analysis strictly in HINDI (हिंदी language using Devanagari script).

User Metrics:
{metrics_summary}

Use this exact Markdown structure:
### 🩺 **आपकी सेहत का हाल (Overall Health)**
(2 simple sentences in easy Hindi explaining overall health status)

### 🌟 **क्या बहुत अच्छा है (What is Good)**
- (Bullet point 1 in simple Hindi with emoji)
- (Bullet point 2 in simple Hindi with emoji)

### ⚠️ **ध्यान देने योग्य बातें (Needs Attention)**
- (Bullet point 1 in simple Hindi with emoji)
- (Bullet point 2 in simple Hindi with emoji)

### 🚀 **आसान 3 कदम आज ही अपनाएं (Simple 3-Step Action Plan)**
1. (Step 1 in easy Hindi)
2. (Step 2 in easy Hindi)
3. (Step 3 in easy Hindi)

Keep sentences short, warm, and super easy for any Hindi reader!
"""
    elif lang == "hinglish":
        prompt = f"""
You are a warm, friendly health coach.
Write a VERY SIMPLE, clear health analysis strictly in HINGLISH (Hindi written using Roman English script, e.g. "Aapki health achhi hai. Bas sleep hours thode badhayein.").

User Metrics:
{metrics_summary}

Use this exact Markdown structure:
### 🩺 **Aapki Health Ka Haal (Overall Health)**
(2 simple sentences in Hinglish explaining overall health status)

### 🌟 **Kya Achha Hai (What is Good)**
- (Bullet point 1 in simple Hinglish with emoji)
- (Bullet point 2 in simple Hinglish with emoji)

### ⚠️ **Kahan Dhyan Dena Hai (Needs Attention)**
- (Bullet point 1 in simple Hinglish with emoji)
- (Bullet point 2 in simple Hinglish with emoji)

### 🚀 **Aasaan 3 Steps Aaj Hi Karen (Simple 3-Step Action Plan)**
1. (Step 1 in easy Hinglish)
2. (Step 2 in easy Hinglish)
3. (Step 3 in easy Hinglish)

Keep sentences short, friendly, and super easy to read!
"""
    else: # English
        prompt = f"""
You are a warm, friendly health coach.
Write a VERY SIMPLE, clear health analysis in 5th-grade level ENGLISH. Avoid complex medical terms.

User Metrics:
{metrics_summary}

Use this exact Markdown structure:
### 🩺 **Your Health Summary**
(2 simple sentences explaining overall health status)

### 🌟 **What is Going Great**
- (Bullet point 1 in simple English with emoji)
- (Bullet point 2 in simple English with emoji)

### ⚠️ **What Needs a Little Care**
- (Bullet point 1 in simple English with emoji)
- (Bullet point 2 in simple English with emoji)

### 🚀 **Easy 3-Step Action Plan**
1. (Step 1 in easy English)
2. (Step 2 in easy English)
3. (Step 3 in easy English)

Keep sentences short, encouraging, and super easy to understand!
"""

    analysis_text = call_gemini_with_backoff(prompt)

    if not analysis_text:
        analysis_text = get_static_simple_analysis(lang, sleep, stress, steps)

    return jsonify({"analysis": analysis_text, "language": lang})


@app.route("/admin-dashboard")
@admin_required
def admin_dashboard():
    return render_view("views/admin_dashboard.html")

@app.route("/api/admin/users")
@admin_required
def admin_api_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.role, u.is_restricted, u.is_deleted, p.age, p.gender, p.goal, u.is_premium
        FROM users u
        LEFT JOIN user_profiles p ON u.id = p.user_id
    ''')
    users = []
    for row in c.fetchall():
        users.append({
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'is_restricted': bool(row[3]),
            'is_deleted': bool(row[4]),
            'age': row[5],
            'gender': row[6],
            'goal': row[7],
            'is_premium': bool(row[8] if len(row) > 8 else 0)
        })
    conn.close()
    return jsonify({'users': users})

@app.route("/api/admin/user/<int:user_id>/restrict", methods=["POST"])
@admin_required
def admin_restrict_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Cannot restrict yourself'}), 400
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT is_restricted FROM users WHERE id=?", (user_id,))
    res = c.fetchone()
    if not res:
        conn.close()
        return jsonify({'error': 'User not found'}), 404
    new_status = 0 if res[0] else 1
    c.execute("UPDATE users SET is_restricted=? WHERE id=?", (new_status, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'is_restricted': bool(new_status)})

@app.route("/api/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    data = request.json or {}
    hard_delete = data.get('hard_delete', False)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    if hard_delete:
        # Hard delete from all tables
        c.execute("DELETE FROM health_logs WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM goals WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM reports WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM notifications WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM user_profiles WHERE user_id=?", (user_id,))
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
    else:
        # Soft delete
        c.execute("UPDATE users SET is_deleted=1 WHERE id=?", (user_id,))
        
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'hard_delete': hard_delete})

@app.route("/api/admin/user/<int:user_id>/toggle-premium", methods=["POST"])
@admin_required
def admin_toggle_premium(user_id):
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT is_premium FROM users WHERE id=?", (user_id,))
        res = c.fetchone()
        if not res:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        current_val = res[0] if res[0] is not None else 0
        new_status = 0 if current_val == 1 else 1
        c.execute("UPDATE users SET is_premium=? WHERE id=?", (new_status, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_premium': bool(new_status)})
    except Exception as e:
        print("Toggle Premium Error:", e)
        return jsonify({'error': str(e)}), 500

@app.route("/admin")
@admin_required
def admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        SELECT u.id, u.username, u.role, u.is_restricted, u.is_deleted, p.age, p.gender, p.goal, u.is_premium
        FROM users u
        LEFT JOIN user_profiles p ON u.id = p.user_id
    ''')
    users = c.fetchall()

    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM health_logs")
    total_assessments = c.fetchone()[0]
    
    c.execute("SELECT AVG(stress_level), AVG(sleep_hours) FROM health_logs")
    avg_data = c.fetchone()
    avg_stress = round(avg_data[0] or 0, 1)
    avg_sleep = round(avg_data[1] or 0, 1)
    
    c.execute("SELECT goal, COUNT(goal) as count FROM health_logs GROUP BY goal ORDER BY count DESC LIMIT 1")
    top_goal_row = c.fetchone()
    top_goal = top_goal_row[0].replace('_', ' ').title() if top_goal_row else "N/A"

    conn.close()
    return render_template("admin.html", users=users, total_users=total_users, total_assessments=total_assessments, avg_stress=avg_stress, avg_sleep=avg_sleep, top_goal=top_goal)


# ==========================================
# LOAD MODEL
# ==========================================
model = pickle.load(open("model.pkl", "rb"))
encoders = pickle.load(open("input_encoders.pkl", "rb"))
target_encoders = pickle.load(open("output_encoders.pkl", "rb"))

target_cols = [
    "workout_plan",
    "diet_plan",
    "lifestyle_change",
    "mental_care",
    "hair_skin_care"
]


# ==========================================
# SECURE GEMINI SETUP & RETRY LOGIC
# ==========================================
def get_gemini_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        for m in models:
            if "generateContent" in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print("Error initializing Gemini client:", str(e))
        return None

def call_gemini_with_backoff(prompt, max_retries=2, initial_delay=1.0):
    """
    Executes a Gemini API request with exponential backoff for HTTP 429 rate limits & transient errors.
    Limits retries to max_retries to prevent worsening quota exhaustion.
    Never exposes API keys or raw error details.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY environment variable is not configured.")
        return None

    model = get_gemini_model()
    if not model:
        print("Gemini model initialization failed or returned None.")
        return None

    delay = initial_delay
    for attempt in range(max_retries + 1):
        try:
            res = model.generate_content(prompt)
            if res and hasattr(res, 'text') and res.text:
                return res.text
        except Exception as e:
            err_str = str(e).lower()
            is_rate_limit = ("429" in err_str or "resource_exhausted" in err_str or "quota" in err_str or "rate limit" in err_str)
            is_transient = ("timeout" in err_str or "503" in err_str or "500" in err_str or "connection" in err_str)

            if is_rate_limit or is_transient:
                print(f"Gemini API attempt {attempt + 1}/{max_retries + 1} failed (Rate limit/Transient error). Retrying in {delay}s...")
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2
                else:
                    print("Max Gemini retries reached. Triggering safe fallback.")
                    return None
            else:
                print("Gemini API non-retryable error encountered:", str(e))
                return None

    return None


# ==========================================
# PREDICTION
# ==========================================
def predict_user(data):
    if not isinstance(data, dict):
        data = {}

    # Sanitize goal for cached frontends
    if 'goal' in data:
        val = str(data['goal']).lower()
        if val == "muscle gain": data['goal'] = "muscle_gain"
        elif val == "weight loss": data['goal'] = "weight_loss"
        elif val == "stress relief": data['goal'] = "stress_relief"

    data_for_df = data.copy()
    data_for_df.pop('language', None)
    data_for_df.pop('timestamp', None)
    data_for_df.pop('userData', None)
    data_for_df.pop('prediction', None)
    
    df = pd.DataFrame([data_for_df])

    # Ensure all expected feature columns are present
    expected_cols = getattr(model, 'feature_names_in_', None)
    if expected_cols is None and hasattr(model, 'estimators_') and len(model.estimators_) > 0:
        expected_cols = getattr(model.estimators_[0], 'feature_names_in_', None)

    if expected_cols is not None:
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = df[expected_cols]

    for col in encoders:
        if col in df.columns:
            try:
                df[col] = encoders[col].transform(df[col])
            except Exception:
                # Fallback for unseen labels
                df[col] = 0

    pred = model.predict(df)

    result = {}
    for i, col in enumerate(target_cols):
        val = target_encoders[col].inverse_transform([pred[0][i]])[0]
        if pd.isna(val):
            val = "No specific plan"
        result[col] = val

    return result



# ==========================================
# SIMPLE PLAN
# ==========================================
SUGGESTIONS = {
    "Light Cardio": ["Walk 6000 steps", "15 min brisk walk"],
    "Low Carb": ["Avoid sugar", "Eat protein"],
    "Improve Sleep": ["Sleep before 11 PM", "No screens"],
    "Meditation": ["10 min meditation", "Deep breathing"],
    "Hydration": ["Drink 2.5L water"]
}

def generate_plan(prediction):
    plan = {}
    for key, value in prediction.items():
        plan[key] = SUGGESTIONS.get(value, ["Maintain routine"])
    return plan


# ==========================================
# COMBINED SINGLE-REQUEST AI GENERATOR
# ==========================================
def get_combined_ai_analysis(user, pred, language='en'):
    """
    Combines root cause, explanation, workout, diet, lifestyle, mental care, and hair/skin recommendations
    into ONE single Gemini API request to optimize quota usage and eliminate unnecessary requests.
    """
    prompt = f"""
You are an expert clinical health, dermatological, and lifestyle AI coach for WellnessIQ.
Provide a warm, encouraging, realistic, and highly actionable analysis combining root causes and specialized recommendations based on the user's data and machine learning predictions.

User Health Metrics:
- Age: {user.get('age', 'N/A')} | Gender: {user.get('gender', 'N/A')} | Weight: {user.get('weight', 'N/A')} kg
- Primary Goal: {user.get('goal', 'N/A')}
- Sleep Duration: {user.get('sleep_hours', 'N/A')} hours
- Stress Level: {user.get('stress_level', 'N/A')}/10
- Daily Steps: {user.get('steps_walked', 'N/A')}
- Daily Exercise: {user.get('exercise_minutes', 'N/A')} mins
- Hydration (Water): {user.get('water_intake', 'N/A')} L
- Dietary Intake: {user.get('calories_intake', 'N/A')} kcal, {user.get('protein_intake', 'N/A')}g protein

ML Model Baseline Recommendations:
- Workout Plan Baseline: {pred.get('workout_plan', 'N/A')}
- Diet Plan Baseline: {pred.get('diet_plan', 'N/A')}
- Lifestyle Change Baseline: {pred.get('lifestyle_change', 'N/A')}
- Mental Care Baseline: {pred.get('mental_care', 'N/A')}
- Hair & Skin Care Baseline: {pred.get('hair_skin_care', 'N/A')}

CRITICAL RULES:
1. Tone must be warm, empowering, realistic, and easy to understand.
2. Be extremely concise. Use short bullet points only. Zero filler words.
3. Reuse the ML predictions to refine and structure recommendations.

Format your output into EXACTLY these 7 sections (using ## headers):

## 🩺 Root Causes & Health Assessment
(2-3 concise bullet points identifying underlying causes of current health markers)

## 📖 Overall Health Explanation
(2 short sentences summarizing overall health status based on metrics)

## ⚡ Workout Recommendation
(Actionable exercise guidance based on the ML workout baseline)

## 🍎 Diet Recommendation
(Practical dietary adjustments based on the ML diet baseline)

## 🌿 Lifestyle Recommendation
(Actionable lifestyle & sleep habits based on the ML lifestyle baseline)

## 🧠 Mental Wellness Recommendation
(Concise mindfulness and stress recovery tips based on the ML mental care baseline)

## ✨ Hair & Skin-Care Guidance
(Actionable dermatological & hair care steps based on the ML hair/skin care baseline)
"""
    if language == 'hi':
        prompt += "\n\nIMPORTANT: You MUST output your ENTIRE response in Hindi (Devanagari script). Use natural, conversational Hindi."

    res_text = call_gemini_with_backoff(prompt)
    if res_text:
        return res_text, False
    else:
        return generate_combined_fallback(user, pred), True


def generate_combined_fallback(user, pred):
    sleep = user.get("sleep_hours", 7)
    stress = user.get("stress_level", 5)
    steps = user.get("steps_walked", 5000)
    water = user.get("water_intake", 2.0)

    causes = []
    if sleep < 6.5:
        causes.append("Insufficient sleep recovery affecting daytime energy levels.")
    if stress > 6:
        causes.append("Elevated stress levels triggering physical and mental fatigue.")
    if steps < 6000:
        causes.append("Sub-optimal physical activity impacting metabolic rate.")
    if water < 2.0:
        causes.append("Low hydration levels affecting skin moisture and concentration.")
    if not causes:
        causes.append("Overall lifestyle metrics are balanced; maintain current consistency.")

    causes_text = "".join([f"- {c}\n" for c in causes])

    return f"""> ℹ️ *AI analysis is temporarily unavailable. Showing recommendations based on your assessment.*

## 🩺 Root Causes & Health Assessment
{causes_text}
## 📖 Overall Health Explanation
Your current baseline assessment combines your daily health logs with our machine learning models to highlight actionable focus areas.

## ⚡ Workout Recommendation
- **Baseline Plan**: {pred.get('workout_plan', 'Light Cardio')}
- Aim for at least {user.get('exercise_minutes', 20)} minutes of continuous movement daily.

## 🍎 Diet Recommendation
- **Baseline Plan**: {pred.get('diet_plan', 'Low Carb / Balanced')}
- Ensure adequate protein intake ({user.get('protein_intake', 50)}g) and focus on whole nutrient-dense foods.

## 🌿 Lifestyle Recommendation
- **Baseline Plan**: {pred.get('lifestyle_change', 'Improve Sleep')}
- Prioritize going to bed at a regular time and limiting screen time 30 minutes before sleep.

## 🧠 Mental Wellness Recommendation
- **Baseline Plan**: {pred.get('mental_care', 'Meditation & Deep Breathing')}
- Practice 5–10 minutes of daily mindfulness or deep breathing breaks to manage stress.

## ✨ Hair & Skin-Care Guidance
- **Baseline Plan**: {pred.get('hair_skin_care', 'Hydration & Scalp Care')}
- Maintain at least {water}L daily water intake to support skin elasticity and scalp nourishment.
"""


def root_ai(user, pred, language='en'):
    ai_text, is_fallback = get_combined_ai_analysis(user, pred, language=language)
    return ai_text

def hair_skin_ai(user, pred, language='en'):
    prompt = f"""
You are an expert Dermatologist and Trichologist AI coach with a warm, encouraging, and user-friendly tone. Provide a highly realistic and easy-to-understand assessment of the user's hair and skin health based on their data.

User Profile:
- Age: {user.get('age', 'N/A')} | Gender: {user.get('gender', 'N/A')} | Weight: {user.get('weight', 'N/A')} kg
- Sleep: {user.get('sleep_hours', 'N/A')} hours
- Stress Level: {user.get('stress_level', 'N/A')}/10
- Water Intake: {user.get('water_intake', 'N/A')} L
- Diet: {user.get('calories_intake', 'N/A')} kcal

ML Model Baseline Hair & Skin Recommendation:
{pred.get('hair_skin_care', 'N/A')}

CRITICAL RULES:
1. Tone must be warm, encouraging, realistic, and easy to understand.
2. Be extremely concise. Use short bullet points only. Zero fluff.

Include EXACTLY these 3 sections (use exactly ## for headings):

## ✨ Skin Glow Analysis
(2-3 concise, realistic tips on how their stress, sleep, and hydration are affecting their skin)

## 💆 Hair Health Insights
(2-3 concise, actionable tips on protecting and nourishing their hair based on the ML baseline)

## 💧 Hydration & Recovery Routine
(1-2 easy daily steps to improve both hair and skin)
"""
    if language == 'hi':
        prompt += "\n\nIMPORTANT: You MUST output your ENTIRE response in Hindi (Devanagari script). Use natural, conversational Hindi."

    res_text = call_gemini_with_backoff(prompt)
    if res_text:
        return res_text
    return f"> ℹ️ *AI analysis is temporarily unavailable. Showing recommendations based on your assessment.*\n\n## ✨ Hair & Skin Baseline\n- Maintain adequate daily hydration ({user.get('water_intake', 2.0)}L) and keep stress managed to support skin and scalp health."

def fallback(user):
    return generate_combined_fallback(user, {})


# ==========================================
# SECURE ROOT CAUSE AI ENDPOINT
# ==========================================
@app.route("/api/ai/root-cause", methods=["POST"])
@login_required
def api_ai_root_cause():
    """
    Secure Backend Gemini Endpoint:
    Frontend -> WellnessIQ Backend -> Gemini API.
    Reads GEMINI_API_KEY from environment, executes combined AI request with backoff,
    and returns structured recommendations without exposing API key.
    """
    try:
        data = request.get_json(force=True) or {}
        user_data = data.get("userData") or data
        lang = data.get("language", "en")
        
        # Calculate ML prediction baseline
        prediction = data.get("prediction")
        if not prediction:
            prediction = predict_user(user_data)
            
        ai_markdown, is_fallback = get_combined_ai_analysis(user_data, prediction, language=lang)
        
        response_payload = {
            "status": "fallback" if is_fallback else "success",
            "prediction": prediction,
            "ai_markdown": ai_markdown,
            "root_cause_analysis": ai_markdown,
            "is_fallback": is_fallback
        }
        if is_fallback:
            response_payload["message"] = "AI analysis is temporarily unavailable. Showing recommendations based on your assessment."

        return jsonify(response_payload)
    except Exception as e:
        print("Error in /api/ai/root-cause:", str(e))
        user_data = request.get_json(silent=True) or {}
        pred = predict_user(user_data) if user_data else {}
        return jsonify({
            "status": "fallback",
            "prediction": pred,
            "ai_markdown": generate_combined_fallback(user_data, pred),
            "root_cause_analysis": generate_combined_fallback(user_data, pred),
            "is_fallback": True,
            "message": "AI analysis is temporarily unavailable. Showing recommendations based on your assessment."
        })


# ==========================================
# API ENDPOINTS
# ==========================================
@app.route("/predict", methods=["POST"])
def predict():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.get_json(force=True)
        
        # Log health data
        user_id = session['user_id']
        goal = data.get('goal', 'unknown')
        sleep = float(data.get('sleep_hours', 0))
        stress = float(data.get('stress_level', 0))
        steps = int(data.get('steps_walked', 0))
        weight = float(data.get('weight', 0))
        water_intake = float(data.get('water_intake', 0))
        screen_time = float(data.get('screen_time', 0))
        work_hours = float(data.get('work_hours', 0))
        protein_intake = float(data.get('protein_intake', 0))
        calories_intake = float(data.get('calories_intake', 0))
        exercise_minutes = float(data.get('exercise_minutes', 0))
        meditation_minutes = float(data.get('meditation_minutes', 0))
        gender = str(data.get('gender', 'unknown'))
        age = int(data.get('age', 0))
        
        try:
            conn = get_db()
            c = conn.cursor()

            c.execute('''
                INSERT INTO health_logs (
                    user_id, goal, sleep_hours, stress_level, steps_walked,
                    weight, water_intake, screen_time, work_hours,
                    protein_intake, calories_intake, exercise_minutes, meditation_minutes, gender
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, goal, sleep, stress, steps, weight, water_intake, screen_time, work_hours, protein_intake, calories_intake, exercise_minutes, meditation_minutes, gender))
            
            c.execute("INSERT OR REPLACE INTO user_profiles (user_id, age, gender, weight, goal) VALUES (?, ?, ?, ?, ?)",
                      (user_id, age, gender, weight, goal))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as db_err:
            print("DB write deferred due to lock:", db_err)


        prediction = predict_user(data)
        lang = data.get('language', 'en')

        ai_markdown, is_fallback = get_combined_ai_analysis(data, prediction, language=lang)

        return jsonify({
            "prediction": prediction,
            "ai_markdown": ai_markdown,
            "is_fallback": is_fallback
        })

    except Exception as e:
        print("Predict endpoint error:", str(e))
        return jsonify({"error": "Failed to process health assessment."}), 500

@app.route("/api/profile")
@login_required
def api_profile():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM user_profiles WHERE user_id=?", (session['user_id'],))
    profile = c.fetchone()
    
    c.execute("SELECT * FROM health_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (session['user_id'],))
    latest_log = c.fetchone()
    conn.close()
    
    res = {}
    if profile: res.update(dict(profile))
    if latest_log:
        log_dict = dict(latest_log)
        log_dict.pop('id', None)
        log_dict.pop('user_id', None)
        log_dict.pop('timestamp', None)
        res.update(log_dict)
    return jsonify(res)

@app.route("/api/history")
@login_required
def api_history():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM health_logs WHERE user_id=? ORDER BY timestamp ASC", (session['user_id'],))
    logs = [dict(row) for row in c.fetchall()]
    
    c.execute("SELECT age, gender, weight, goal FROM user_profiles WHERE user_id=?", (session['user_id'],))
    prof = c.fetchone()
    conn.close()
    
    if prof:
        for log in logs:
            if not log.get('weight'): log['weight'] = prof['weight']
            if not log.get('goal') or log.get('goal') == 'unknown': log['goal'] = prof['goal']
            
    return jsonify({"history": logs, "profile": dict(prof) if prof else {}})

@app.route("/analysis/<analysis_type>")
@login_required
def analysis_page(analysis_type):
    return render_template("analysis.html", analysis_type=analysis_type)

@app.route("/predict-hair-skin", methods=["POST"])
def predict_hair_skin():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = request.get_json(force=True)
        prediction = predict_user(data)
        lang = data.get('language', 'en')
        
        ai_markdown = hair_skin_ai(data, prediction, language=lang)
            
        return jsonify({
            "prediction": prediction,
            "ai_markdown": ai_markdown
        })
    except Exception as e:
        print("Predict Hair Skin Error:", str(e))
        return jsonify({
            "prediction": predict_user(request.get_json(silent=True) or {}),
            "ai_markdown": "> ℹ️ *AI analysis is temporarily unavailable. Showing recommendations based on your assessment.*\n\n## ✨ Hair & Skin Baseline\n- Maintain adequate daily hydration and manage stress to support skin and scalp health."
        })

# ==========================================
# DETAILED ANALYSIS AI (GEMINI)
# ==========================================
def generate_detailed_analysis(user, pred, analysis_type, answers, language='en'):
    profile = f"""
    Age: {user.get('age', 'N/A')} | Weight: {user.get('weight', 'N/A')} kg | Gender: {user.get('gender', 'N/A')}
    Goal: {user.get('goal', 'N/A')}
    Sleep: {user.get('sleep_hours', 'N/A')} hrs | Stress: {user.get('stress_level', 'N/A')}/10
    """

    prompts = {
        "workout": f"""
You are an expert Fitness Coach.
User Profile: {profile}
Base Recommendation: {pred.get('workout_plan', 'N/A')}
User Specific Answers: {answers}

Requirements:
- Provide ONLY a short Summary (2-3 sentences).
- If the user has access to gym equipment (check 'User Specific Answers'), provide a Weekly Gym Workout Plan.
- If the user has NO equipment, provide a Daily Home Workout Plan.
- Format the plan strictly as a beautifully formatted Markdown table (e.g. Columns for Day/Time, Exercise, Sets/Reps, Notes).
""",
        "diet": f"""
You are an expert Clinical Nutritionist.
User Profile: {profile}
Base Recommendation: {pred.get('diet_plan', 'N/A')}
User Specific Answers: {answers}

Requirements:
- Provide ONLY a short Summary (2-3 sentences).
- Provide a Daily Diet Plan.
- Format the plan strictly as a beautifully formatted Markdown table (e.g. Columns for Meal, Food Item, Macros, Notes).
""",
        "lifestyle": f"""
You are an expert Lifestyle Coach.
User Profile: {profile}
Base Recommendation: {pred.get('lifestyle_change', 'N/A')}
User Specific Answers: {answers}

Requirements:
- Provide ONLY a short Summary (2-3 sentences).
- Provide a Daily Lifestyle Routine.
- Format the routine strictly as a beautifully formatted Markdown table (e.g. Columns for Time, Activity, Duration, Benefits).
""",
        "mental": f"""
You are an expert Mental Wellness Coach.
User Profile: {profile}
Base Recommendation: {pred.get('mental_care', 'N/A')}
User Specific Answers: {answers}

Requirements:
- Provide ONLY a short Summary (2-3 sentences).
- Provide a Daily Mental Wellness Routine.
- Format the routine strictly as a beautifully formatted Markdown table (e.g. Columns for Time, Activity, Duration, Goal).
""",
        "hair_skin": f"""
You are an expert Dermatologist.
User Profile: {profile}
Base Recommendation: {pred.get('hair_skin_care', 'N/A')}
User Specific Answers: {answers}

Requirements:
- Provide ONLY a short Summary (2-3 sentences).
- Provide a Daily Hair & Skin Care Routine.
- Format the routine strictly as a beautifully formatted Markdown table (e.g. Columns for Time, Step, Product/Action, Details).
"""
    }

    prompt_text = prompts.get(analysis_type, prompts["lifestyle"])
    prompt_text += "\nFormat the response beautifully in Markdown with emojis and clear headers. Do not use generic filler words."
    
    if language == 'hi':
        prompt_text += "\n\nIMPORTANT: You MUST output your ENTIRE response in Hindi (Devanagari script). Use natural, conversational Hindi."

    res_text = call_gemini_with_backoff(prompt_text)
    if res_text:
        return res_text
    return "> ℹ️ *AI analysis is temporarily unavailable. Showing recommendations based on your assessment.*\n\n## ⚠️ Detailed Analysis Unavailable\nCould not fetch detailed deep-dive analysis at this time. Please refer to your dashboard baseline recommendations."

def is_user_premium(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT is_premium FROM users WHERE id=?", (user_id,))
    res = c.fetchone()
    conn.close()
    return bool(res[0]) if res else False

@app.route("/analyze-detail", methods=["POST"])
@login_required
def analyze_detail():
    user_id = session.get('user_id')
    if not is_user_premium(user_id):
        return jsonify({
            "status": "premium_required",
            "error": "Premium Feature Locked",
            "message": "Deep Dive Analysis is exclusive to Premium Users. The first 50 registered users received complimentary premium access. To request premium access, please mail your reason for usage request to rastogi21yr@gmail.com.",
            "contact_email": "rastogi21yr@gmail.com"
        }), 403

    try:
        data = request.get_json(force=True)
        user_data = data.get("userData", {})
        prediction = data.get("prediction", {})
        analysis_type = data.get("type", "lifestyle")
        answers = data.get("answers", {})
        lang = data.get("language", "en")

        ai_markdown = generate_detailed_analysis(user_data, prediction, analysis_type, answers, language=lang)
        return jsonify({"ai_markdown": ai_markdown})
    except Exception as e:
        print("Analyze detail error:", str(e))
        return jsonify({"error": "Failed to process detailed analysis."}), 500



@app.route("/api/goals", methods=["GET", "POST", "DELETE"])
@login_required
def api_goals():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if request.method == "GET":
        c.execute("SELECT * FROM goals WHERE user_id=? AND status='active'", (session['user_id'],))
        goals = [dict(r) for r in c.fetchall()]
        
        c.execute("SELECT * FROM health_logs WHERE user_id=? ORDER BY timestamp DESC LIMIT 1", (session['user_id'],))
        last_log = c.fetchone()
        
        if last_log:
            last_log = dict(last_log)
            for g in goals:
                cat = g['category']
                if cat == 'Sleep goal': g['progress'] = last_log.get('sleep_hours', 0)
                elif cat == 'Water goal': g['progress'] = last_log.get('water_intake', 0)
                elif cat == 'Weight goal': g['progress'] = last_log.get('weight', 0)
                elif cat == 'Exercise goal': g['progress'] = last_log.get('exercise_minutes', 0)
                elif cat == 'Meditation goal': g['progress'] = last_log.get('meditation_minutes', 0)
        
        conn.close()
        return jsonify({"goals": goals})
        
    elif request.method == "POST":
        data = request.json
        c.execute("INSERT INTO goals (user_id, category, target, unit) VALUES (?, ?, ?, ?)",
                  (session['user_id'], data.get('category'), data.get('target'), data.get('unit')))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
        
    elif request.method == "DELETE":
        c.execute("UPDATE goals SET status='deleted' WHERE id=? AND user_id=?", (request.json.get('id'), session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({"success": True})

# ==========================================
# RUN
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)