import os
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pandas as pd

def train_model(data, model_type="linear"):
    """
    Train a regression model to predict cognitive load (MWS).

    Args:
        data (tuple): A tuple containing (X_train, X_test, y_train, y_test).
        model_type (str): The type of model to train ("linear" or "random_forest").

    Returns:
        model: The trained model.
    """
    X_train, X_test, y_train, y_test = data

    # Choose the model
    if model_type == "linear":
        model = LinearRegression()
    elif model_type == "random_forest":
        model = RandomForestRegressor(random_state=42)
    else:
        raise ValueError("Invalid model_type. Choose 'linear' or 'random_forest'.")

    # Train the model
    model.fit(X_train, y_train)

    # Evaluate the model
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model Type: {model_type}, Mean Squared Error: {mse}")

    # Save the model to a file
    models_dir = os.path.join(os.path.dirname(__file__), "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "cognitive_load_model.pkl")
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model

def predict(model, new_data):
    """
    Predict cognitive load (MWS) for new data.

    Args:
        model: The trained model.
        new_data (dict): A dictionary containing 'Time' and 'Errors' values.

    Returns:
        float: Predicted MWS value.
    """
    # Convert new_data to a DataFrame
    new_data_df = pd.DataFrame([new_data])

    # Predict MWS
    prediction = model.predict(new_data_df)
    return prediction[0]

if __name__ == "__main__":
    from data_preprocessing import preprocess_data

    # Load and preprocess the data
    file_path = os.path.join(os.path.dirname(__file__), '../data/pizza_dataset/PrevExperimentData.csv')
    data = preprocess_data(file_path)

    # Train the model
    model = train_model(data, model_type="linear")
    print("Model training complete.")