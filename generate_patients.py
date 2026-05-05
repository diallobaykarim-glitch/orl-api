import requests
import random

URL = "http://localhost:8000/predict"

for i in range(1, 112):
    data = {
        "id": 1000 + i,
        "age": random.randint(20, 90),
        "larynx": random.randint(0, 1),
        "parotide": random.randint(0, 1),
        "ethmoide": random.randint(0, 1)
    }

    r = requests.post(URL, json=data)
    print(i, r.json())