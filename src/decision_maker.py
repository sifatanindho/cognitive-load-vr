def recommend_task(cognitive_load):
    """
    Recommend a task difficulty level based on the predicted cognitive load.

    Args:
        cognitive_load (str): Predicted cognitive load category (e.g., "Very Low", "Low", "Medium", "High", "Very High").

    Returns:
        int: Recommended task difficulty level (1-5).
    """
    # Define the mapping of cognitive load to task difficulty
    load_to_difficulty = {
        "Very Low": 5,  # Increase difficulty to challenge the user
        "Low": 4,
        "Medium": 3,    # Keep difficulty moderate
        "High": 2,
        "Very High": 1  # Reduce difficulty to avoid overwhelming the user
    }

    # Return the recommended task difficulty
    return load_to_difficulty.get(cognitive_load, 3)  # Default to Medium if input is invalid

if __name__ == "__main__":
    # Example usage
    predicted_load = "High"  # Example input
    recommended_task = recommend_task(predicted_load)
    print(f"Predicted Cognitive Load: {predicted_load}")
    print(f"Recommended Task Difficulty: {recommended_task}")