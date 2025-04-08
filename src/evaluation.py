import os
import pickle
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the performance of a trained classification model.

    Args:
        model: The trained classification model.
        X_test (DataFrame): The test features.
        y_test (Series): The true target labels for the test set.

    Returns:
        dict: A dictionary containing evaluation metrics (accuracy, classification report, confusion matrix).
    """
    # Predict the target labels for the test set
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    class_report = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)

    # Print the metrics
    print(f"Accuracy: {accuracy}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    print(conf_matrix)

    # Return the metrics as a dictionary
    return {"accuracy": accuracy, "classification_report": class_report, "confusion_matrix": conf_matrix}

if __name__ == "__main__":
    # Resolve paths dynamically
    base_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(base_dir, "../data/processed")
    models_dir = os.path.join(base_dir, "../models")

    # Paths for test data
    X_test_path = os.path.join(processed_dir, "X_test.csv")
    y_test_path = os.path.join(processed_dir, "y_test.csv")

    # Load the test data
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path).squeeze()  # Convert to Series

    # Path for the trained model
    model_path = os.path.join(models_dir, "cognitive_load_model.pkl")

    # Load the trained model
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    # Evaluate the model
    metrics = evaluate_model(model, X_test, y_test)
    print("Evaluation complete.")