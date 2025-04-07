import os
import pickle
import pandas as pd

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def evaluate_model(model, X_test, y_test):
    """
    Evaluate the performance of a trained regression model.

    Args:
        model: The trained regression model.
        X_test (DataFrame): The test features.
        y_test (Series): The true target values for the test set.

    Returns:
        dict: A dictionary containing evaluation metrics (MSE, MAE, R²).
    """
    # Predict the target values for the test set
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Print the metrics
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"R-squared (R²): {r2}")

    # Return the metrics as a dictionary
    return {"MSE": mse, "MAE": mae, "R2": r2}

if __name__ == "__main__":
    

    # Load the test data
    X_test_path = os.path.join(os.path.dirname(__file__), "../data/processed/X_test.csv")
    y_test_path = os.path.join(os.path.dirname(__file__), "../data/processed/y_test.csv")
    X_test = pd.read_csv(X_test_path)
    y_test = pd.read_csv(y_test_path).squeeze()  # Convert to Series

    # Load the trained model
    model_path = os.path.join(os.path.dirname(__file__), "../models/cognitive_load_model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    # Evaluate the model
    metrics = evaluate_model(model, X_test, y_test)
    print("Evaluation complete.")