import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score
import numpy as np
import pandas as pd

from data_preprocessing import preprocess_data

def train_model(data, model_type="random_forest"):
    """
    Train a classification model to predict cognitive load labels with cross-validation.

    Args:
        data (tuple): A tuple containing (X_train, X_test, y_train, y_test).
        model_type (str): The type of model to train ("random_forest" or "logistic_regression").

    Returns:
        model: The trained model.
    """
    X_train, X_test, y_train, y_test = data

    # Choose the model
    if model_type == "random_forest":
        model = RandomForestClassifier(random_state=42)
    elif model_type == "logistic_regression":
        model = LogisticRegression(max_iter=1000, random_state=42)
    else:
        raise ValueError("Invalid model_type. Choose 'random_forest' or 'logistic_regression'.")

    # Perform cross-validation
    print("Performing cross-validation...")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
    print(f"Cross-Validation Scores: {cv_scores}")
    print(f"Mean CV Accuracy: {np.mean(cv_scores)}")
    print(f"Standard Deviation of CV Accuracy: {np.std(cv_scores)}")

    # Train the model on the full training set
    model.fit(X_train, y_train)

    # Evaluate the model on the test set
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Set Accuracy: {accuracy}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save the model to a file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "cognitive_load_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model

def predict(model, new_data):
    """
    Predict cognitive load labels for new data.

    Args:
        model: The trained model.
        new_data (dict): A dictionary containing 'Time' and 'Errors' values.

    Returns:
        str: Predicted cognitive load label.
    """
    # Convert new_data to a DataFrame
    new_data_df = pd.DataFrame([new_data])

    # Predict the label
    prediction = model.predict(new_data_df)
    return prediction[0]

if __name__ == "__main__":

    # Resolve paths dynamically
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../data/pizza_dataset")
    file_path = os.path.join(data_dir, "PrevExperimentData.csv")

    # Load and preprocess the data
    X_train, X_test, y_train, y_test = preprocess_data(file_path)

    # Train the model
    model = train_model((X_train, X_test, y_train, y_test), model_type="logistic_regression")
    print("Model training complete.")