import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score
import numpy as np

df = pd.read_csv("advanced_routine_dataset_1000.csv")

categorical_cols = [
    "gender", "goal", "exercise_type",
    "social_interaction", "water_quality"
]

encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

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

X = df.drop(columns=target_cols + ["user_id"])
y = df[target_cols]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

models = {
    "Baseline RF (Current)": MultiOutputClassifier(RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)),
    "Tuned RF": MultiOutputClassifier(RandomForestClassifier(n_estimators=500, max_depth=20, min_samples_split=2, random_state=42)),
    "HistGradientBoosting": MultiOutputClassifier(HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=42))
}

for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    # Exact match accuracy
    exact_match = np.all(y_pred == y_test.values, axis=1).mean()
    
    # Column-wise accuracy
    col_accs = [accuracy_score(y_test.values[:, i], y_pred[:, i]) for i in range(len(target_cols))]
    mean_col_acc = np.mean(col_accs)
    
    print(f"--- {name} ---")
    print(f"Exact Match Accuracy: {exact_match:.4f}")
    print(f"Mean Column Accuracy: {mean_col_acc:.4f}")
    print()
