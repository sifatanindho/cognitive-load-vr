import argparse
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import sys
import os.path
import joblib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.data_preprocessing import preprocess_data

def train_model(data, model_type="random_forest"):
    X_train, X_test, y_train, y_test = data
    if model_type == "random_forest":
        model = RandomForestClassifier(random_state=42)
    elif model_type == "logistic_regression":
        model = LogisticRegression(max_iter=1000, random_state=42)
    else:
        raise ValueError("Invalid model_type. Choose 'random_forest' or 'logistic_regression'.")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
    print(f"Cross-Validation Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {np.mean(cv_scores)}")
    print(f"Standard Deviation of CV Accuracy: {np.std(cv_scores)}")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {accuracy}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "cognitive_load_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    return model

def predict(model, new_data):
    new_data_df = pd.DataFrame([new_data])
    new_data_df[['Time', 'Errors']] = saved_scaler.transform(new_data_df[['Time', 'Errors']])
    prediction = model.predict(new_data_df)
    return prediction[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="train a cognitive load prediction model bro")
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="This is the path to the dataset CSV file you wanna use. If ya don't provide this, the default pizza dataset will be used."
    )
    parser.add_argument(
        "--model_type",
        type=str,
        default="logistic_regression",
        choices=["random_forest", "logistic_regression"],
        help="Type of model to train. You only got two choices rn :) : 'random_forest' and 'logistic_regression'."
    )
    args = parser.parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../data/pizza_dataset")
    file_path = os.path.join(data_dir, "PrevExperimentData.csv")
    file_path = args.dataset if args.dataset else os.path.join(data_dir, "PrevExperimentData.csv")
    X_train, X_test, y_train, y_test = preprocess_data(file_path)
    saved_scaler = joblib.load('scaler.pkl')
    model = train_model((X_train, X_test, y_train, y_test), model_type=args.model_type)
    print("Model trained babyy.")