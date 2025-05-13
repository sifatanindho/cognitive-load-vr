import os
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib

def evaluate_the_model(model, x_test, y_test):
    y_codes = {"Very Low": 0, "Low": 1, "Medium": 2, "High": 3, "Very High": 4}
    y_pred = model.predict(x_test) 
    y_pred_numeric = pd.Series(y_pred).map(y_codes)
    y_test_numeric = pd.Series(y_test).map(y_codes)
    accuracy = accuracy_score(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    off_by_1 = 0
    for i in range(len(y_test_numeric)):
        if abs(y_test_numeric[i] - y_pred_numeric[i]) <= 1:
            off_by_1 += 1
    off_by_1 = off_by_1 / len(y_test)
    print(f"accuracy: {accuracy}")
    print("\nclassification report:")
    print(classification_report(y_test, y_pred))
    print("\nconfusion matrix:")
    print(conf_matrix)
    print(f"\noff-by-1 Ratio: {off_by_1}")
    return {
        "accuracy": accuracy,
        "classification_report": class_report,
        "confusion_matrix": conf_matrix,
        "off_by_1_ratio": off_by_1,
    }

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(base_dir, "../data/processed")
    models_dir = os.path.join(base_dir, "../models")
    X_test_path = os.path.join(processed_dir, "X_test.csv")
    y_test_path = os.path.join(processed_dir, "y_test.csv")
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path).squeeze()
    model_path = os.path.join(models_dir, "cognitive_load_model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    metrics = evaluate_the_model(model, X_test, y_test)
    print("We done evaluated")