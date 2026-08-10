import requests
import json

data = {
    "age": 25,
    "gender": "Male",
    "weight": 70,
    "height": 175,
    "bmi": 22.9,
    "goal": "weight_loss",
    "sleep_hours": 7,
    "sleep_quality": 2,
    "bedtime_hour": 1,
    "wake_time": 7,
    "fatigue_level": 8,
    "steps_walked": 8000,
    "exercise_minutes": 30,
    "exercise_type": "none",
    "calories_burned": 150,
    "heart_rate_avg": 85,
    "calories_intake": 2500,
    "protein_intake": 60,
    "junk_food_freq": 5,
    "water_intake": 2.5,
    "meal_frequency": 3,
    "stress_level": 5,
    "mood": 4,
    "screen_time": 6,
    "work_hours": 8,
    "social_interaction": "low",
    "meditation_minutes": 10,
    "hair_condition": 2,
    "skin_condition": 2,
    "sun_exposure": 4,
    "water_quality": "average"
}

try:
    res = requests.post("http://127.0.0.1:5000/predict", json=data)
    print("Status Code:", res.status_code)
    print("Response JSON:")
    print(json.dumps(res.json(), indent=2))
except Exception as e:
    print("Error:", str(e))
