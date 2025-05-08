from src.decision_maker import recommend_task, get_number_of_blocks, generate_lego_structure, plot_lego_sides, plot_lego_structure_3d
import pickle
import os

def run_study(last_report):
    experiment_type = last_report.get("experiment_type")
    task_number = last_report.get("task")
    errors = int(last_report.get("errors"))
    duration = float(last_report.get("duration"))
    predicted_load = None
    if experiment_type == "Control":
        control_loads = {
            1: "Medium",
            2: "Very High",
            3: "High",
            4: "Low",
            5: "Medium"
        }
        predicted_load = control_loads.get(task_number, "Medium")
    elif experiment_type == "AI":
        if task_number in [1, 5]:
            predicted_load = "Medium"
        elif task_number in [2, 3, 4]:
            model_path = os.path.join(os.path.dirname(__file__), "models", "cognitive_load_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, "rb") as model_file:
                    model = pickle.load(model_file)
                input_data = [[duration, errors]] 
                predicted_load = model.predict(input_data)[0]
            else:
                print("Cognitive load model not found. Defaulting to 'Medium'.")
                predicted_load = "Medium"
    print(f"Task {task_number}: Predicted Cognitive Load = {predicted_load}")
    recommended_task = recommend_task(predicted_load)
    dimensions = get_number_of_blocks(recommended_task)
    lego_structure = generate_lego_structure(dimensions)
    plot_dir = os.path.join(os.path.dirname(__file__), "lego_images", f"task_{task_number + 1}")
    os.makedirs(plot_dir, exist_ok=True)
    plot_lego_sides(lego_structure, save_path=plot_dir)
    # plot_lego_structure_3d(lego_structure)
    log_message = (
        f"Task {task_number}:\n"
        f"  Experiment Type: {experiment_type}\n"
        f"  Predicted Load: {predicted_load}\n"
        f"  Recommended Task: {recommended_task}\n"
        f"  Dimensions: {dimensions}\n"
        f"  Lego structure saved to: {plot_dir}\n"
    )
    print(log_message)
    log_file = os.path.join(os.path.dirname(__file__), "task_log.txt")
    with open(log_file, "a") as log:
        log.write(log_message)

def main():
    print("Run the user app")