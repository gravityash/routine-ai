# ==========================================
# ROUTINE AI APP (FINAL CLEAN VERSION)
# ==========================================

import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import HistGradientBoostingClassifier

# ==========================================
# LOAD DATASET
# ==========================================
df = pd.read_csv("advanced_routine_dataset_1000.csv")

# ==========================================
# ENCODE INPUT FEATURES
# ==========================================
categorical_cols = [
    "gender", "goal", "exercise_type",
    "social_interaction", "water_quality"
]

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# ==========================================
# ENCODE OUTPUT LABELS
# ==========================================
target_cols = [
    "workout_plan", "diet_plan",
    "lifestyle_change", "mental_care",
    "hair_skin_care"
]

target_encoders = {}
for col in target_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    target_encoders[col] = le

# ==========================================
# SPLIT DATA
# ==========================================
X = df.drop(columns=target_cols + ["user_id"])
y = df[target_cols]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==========================================
# MODEL
# ==========================================
model = MultiOutputClassifier(
    HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=42)
)

model.fit(X_train, y_train)
print("Model trained successfully.")

# ==========================================
# SAVE MODEL
# ==========================================
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(encoders, open("input_encoders.pkl", "wb"))
pickle.dump(target_encoders, open("output_encoders.pkl", "wb"))

# ==========================================
# PREDICTION FUNCTION
# ==========================================
def predict_user(input_data):
    df_input = pd.DataFrame([input_data])

    for col in encoders:
        df_input[col] = encoders[col].transform(df_input[col])

    pred = model.predict(df_input)

    result = {}
    for i, col in enumerate(target_cols):
        result[col] = target_encoders[col].inverse_transform([pred[0][i]])[0]

    return result


# ==========================================
# SUGGESTION ENGINE
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
# GEMINI SETUP (AUTO MODEL DETECTION)
# ==========================================
import google.generativeai as genai

genai.configure(api_key="AIzaSyB9AGCCZxR7-bjS69OYHgd8R40RTIu--Dk")  # 🔑 Replace this


def get_working_model():
    try:
        models = genai.list_models()

        for m in models:
            if "generateContent" in m.supported_generation_methods:
                print("Using model:", m.name)
                return genai.GenerativeModel(m.name)

        raise Exception("No compatible model found")

    except Exception as e:
        print("Model detection failed:", e)
        return None


# ==========================================
# CLEAN OUTPUT FUNCTION
# ==========================================
def clean_root_output(text):
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # remove numbering
        if line[0].isdigit():
            line = line.split(".", 1)[-1].strip()

        cleaned.append("• " + line)

    return "\n".join(cleaned)


# ==========================================
# GEMINI ROOT CAUSE FUNCTION
# ==========================================
def get_root_cause_gemini(user_input, prediction):

    model = get_working_model()

    if model is None:
        raise Exception("No working Gemini model")

    prompt = f"""
Age:{user_input['age']}, Sleep:{user_input['sleep_hours']}, Stress:{user_input['stress_level']}

Workout:{prediction['workout_plan']}
Diet:{prediction['diet_plan']}
Lifestyle:{prediction['lifestyle_change']}

Give 3 short root causes.
Max 8 words each.
"""

    response = model.generate_content(prompt)
    return response.text


# ==========================================
# FALLBACK ROOT CAUSE
# ==========================================
def fallback_root_cause(user):

    causes = []

    if user["sleep_hours"] < 6:
        causes.append("Low sleep affecting energy")

    if user["stress_level"] > 7:
        causes.append("High stress impacting mental health")

    if user["steps_walked"] < 3000:
        causes.append("Low physical activity")

    if user["water_intake"] < 2:
        causes.append("Low hydration affecting body")

    return "\n".join(["• " + c for c in causes])


# ==========================================
# SAMPLE INPUT
# ==========================================
sample_input = {
    "age": 22,
    "gender": "Male",
    "weight": 70,
    "height": 175,
    "bmi": 22.9,
    "goal": "weight_loss",
    "sleep_hours": 5,
    "sleep_quality": 2,
    "bedtime_hour": 1,
    "wake_time": 7,
    "fatigue_level": 8,
    "steps_walked": 2000,
    "exercise_minutes": 0,
    "exercise_type": "none",
    "calories_burned": 150,
    "heart_rate_avg": 85,
    "calories_intake": 3000,
    "protein_intake": 40,
    "junk_food_freq": 5,
    "water_intake": 1.5,
    "meal_frequency": 3,
    "stress_level": 10,
    "mood": 4,
    "screen_time": 8,
    "work_hours": 9,
    "social_interaction": "low",
    "meditation_minutes": 0,
    "hair_condition": 2,
    "skin_condition": 2,
    "sun_exposure": 4,
    "water_quality": "average"
}

# ==========================================
# RUN PIPELINE
# ==========================================
print("\n===== PREDICTION =====")
prediction = predict_user(sample_input)
print(prediction)

print("\n===== PLAN =====")
plan = generate_plan(prediction)

for key, tasks in plan.items():
    print(f"\n{key.upper()}")
    for t in tasks:
        print("-", t)

print("\n===== ROOT CAUSE =====")

try:
    root = get_root_cause_gemini(sample_input, prediction)
    print(clean_root_output(root))

except Exception as e:
    print("Gemini Error:", e)
    print("Using fallback...\n")
    print(fallback_root_cause(sample_input))