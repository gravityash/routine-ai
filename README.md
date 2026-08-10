# Routine AI (WellnessIQ)

Routine AI is a comprehensive, multi-page web application and health ecosystem that leverages Machine Learning and Generative AI to provide personalized health, lifestyle, and wellness recommendations.

## Detailed Features

### 🔐 1. Dual-Role Authentication System
*   **Secure Access**: Password hashing and verification using Werkzeug.
*   **Role Management**: Session-based user authentication. The first registered user automatically becomes an `admin`, while subsequent users are registered as `user`.
*   **Protected Routes**: Custom decorators (`@login_required`, `@admin_required`) ensure secure access to specific pages like the dashboard and admin panel.

### 🧠 2. Core Machine Learning Engine
*   **Predictive Analytics**: Utilizes a trained Scikit-Learn Machine Learning model (`model.pkl`) to generate baseline recommendations based on user inputs (age, gender, weight, goal, sleep hours, stress level, and steps walked).
*   **Holistic Baselines**: Predicts actionable baselines across 5 key areas: Workout, Diet, Lifestyle, Mental Care, and Hair/Skin Care.
*   **Custom Encoders**: Uses pickled label encoders (`input_encoders.pkl`, `output_encoders.pkl`) for robust data transformation.

### 💬 3. Generative AI Coaching (Google Gemini)
*   **Personalized Action Plans**: Transforms clinical ML baselines into warm, conversational, and highly personalized daily plans.
*   **Rich Markdown Output**: Generates beautifully formatted advice including emojis, bullet points, and specific sections (e.g., "🩺 Your Health Baselines", "⚡ Your Actionable Activity Plan").
*   **Fallback Mechanism**: Gracefully falls back to static baseline suggestions if the AI service is temporarily unavailable.

### 📊 4. Advanced 'Detailed Analysis' Module
*   **In-Depth Routines**: Users can request deep-dives into specific areas (Workout, Diet, Lifestyle, Mental Wellness).
*   **Context-Aware**: Adjusts plans based on user-specific answers (e.g., generating a Weekly Gym Workout Plan vs. a Daily Home Workout Plan depending on equipment access).
*   **Structured Tables**: Outputs routines strictly as easy-to-read Markdown tables.

### ✨ 5. Specialized Hair & Skin Care Module
*   **Dedicated AI Persona**: Uses a specialized Dermatologist/Trichologist AI prompt.
*   **Stress & Hydration Analysis**: Analyzes user hydration, stress, and sleep data to generate "Skin Glow Analysis" and "Hair Health Insights".

### 📈 6. Progress Tracking & Health Logging
*   **Automated Logging**: Every prediction request is securely logged into an SQLite database (`health_logs` table).
*   **Historical Context**: Tracks user goals, sleep patterns, stress levels, and daily steps over time to power the progress dashboard.

### 🛡️ 7. Admin Analytics Dashboard
*   **Platform Oversight**: Dedicated view for administrators to monitor overall platform health and usage.
*   **Aggregated Metrics**: Displays total registered users and total health assessments conducted.
*   **Health Averages**: Calculates platform-wide averages for stress levels, sleep hours, and identifies the most common health goals among the user base.

### 🌐 8. Complete Multilingual Support (i18n)
*   **Seamless Switching**: Full support for English and Hindi content generation.
*   **Native Output**: Gemini prompts dynamically adjust to output natural, conversational Hindi (in Devanagari script) across all AI responses when requested by the user.

### 🎨 9. Modern, Responsive Frontend Architecture
*   **Multi-Page Application**: Distinct routes for Home, About, Login, Register, Dashboard, Progress, Admin, and Hair/Skin.
*   **Dynamic UI**: Modern aesthetic built with Vanilla CSS, featuring global theme synchronization (Dark/Light mode persistence).

## Technology Stack

*   **Backend**: Python, Flask, Flask-CORS
*   **Database**: SQLite (`users.db`)
*   **Machine Learning**: Scikit-Learn, Pandas (Pickled models and encoders)
*   **Generative AI**: Google Generative AI (Gemini)
*   **Frontend**: HTML, Vanilla CSS, JavaScript (Jinja2 Templates)

## Project Structure

*   `app.py`: The main Flask application containing routing, authentication, API endpoints, and AI integration logic.
*   `train_model.py`: Script used to train the machine learning models.
*   `evaluate_models.py`: Script to evaluate model performance.
*   `users.db`: SQLite database storing user credentials and health logs.
*   `templates/`: HTML templates for the frontend.
*   `static/`: CSS and JavaScript files for styling and interactivity.
*   `*.pkl`: Pre-trained ML models and encoders (`model.pkl`, `input_encoders.pkl`, `output_encoders.pkl`).
*   `advanced_routine_dataset_1000.csv`: The dataset used to train the ML models.
*   `inject_i18n.py` / `add_data_i18n.py`: Scripts used for adding localization and multilingual capabilities.
*   `fix_styles.py`: Utility script for styling adjustments.

## How to Run Locally

1.  **Install Dependencies**: Ensure you have Python installed, along with the necessary packages (Flask, Pandas, scikit-learn, google-generativeai, etc.).
2.  **Run the Server**: Execute the main application script:
    ```bash
    python app.py
    ```
3.  **Access the App**: Open your web browser and navigate to `http://127.0.0.1:5000`.
