import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

# dataset simple ORL
X = np.array([
    [50, 1, 0, 0],
    [70, 1, 1, 1],
    [30, 0, 0, 0],
    [65, 1, 1, 0],
])

y = np.array([0, 1, 0, 1])  # 0 benign / 1 malignant

model = RandomForestClassifier()
model.fit(X, y)

joblib.dump(model, "model.pkl")

print("Model saved")