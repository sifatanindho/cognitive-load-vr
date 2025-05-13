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

def train_the_model(data, model_type="logistic_regression"):
    x_train, x_test, y_train, y_test = data
    if model_type == "random_forest":
        model = RandomForestClassifier(random_state=45)
    elif model_type == "logistic_regression":
        model = LogisticRegression(max_iter=100000, random_state=45)
    cv_scores = cross_val_score(model, x_train, y_train, cv=5, scoring="accuracy")
    print(f"cross-validation Scores: {cv_scores}")
    print(f"mean cross-val acc: {np.mean(cv_scores)}")
    print(f"stdev of cross-val acc: {np.std(cv_scores)}")
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
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
    # new_data_df[['Time', 'Errors']] = saved_scaler.transform(new_data_df[['Time', 'Errors']])
    prediction = model.predict(new_data_df)
    return prediction[0]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="train a cognitive load prediction model bro")
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="this is the path to the dataset CSV file you wanna use; if ya don't provide this, the default pizza dataset will be used."
    )
    parser.add_argument(
        "--model_type",
        type=str,
        default="logistic_regression",
        choices=["random_forest", "logistic_regression"],
        help="type of model to train; you only got two choices rn :) : 'random_forest' and 'logistic_regression'."
    )
    args = parser.parse_args()
    base_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(base_directory, "../data/pizza_dataset")
    file_path = os.path.join(data_directory, "PrevExperimentData.csv")
    if args.dataset:
        file_path = args.dataset
    else:
        file_path = os.path.join(data_directory, "PrevExperimentData.csv")
    x_train, x_test, y_train, y_test = preprocess_data(file_path)
    saved_scaler = joblib.load('scaler.pkl')
    model = train_the_model((x_train, x_test, y_train, y_test), model_type=args.model_type)
    print("Model trained babyy.")