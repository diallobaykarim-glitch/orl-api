import csv
import os

FILE_NAME = "patients.csv"

def save_patient(data, prediction, proba):

    file_exists = os.path.isfile(FILE_NAME)

    with open(FILE_NAME, mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "age", "larynx", "parotide", "ethmoide",
                "prediction", "probability"
            ])

        writer.writerow([
            data["age"],
            data["larynx"],
            data["parotide"],
            data["ethmoide"],
            prediction,
            proba
        ])
