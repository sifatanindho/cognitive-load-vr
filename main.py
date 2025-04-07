from src.data_preprocessing import preprocess_data
from src.model import train_model, predict
from src.decision_maker import recommend_task

data = preprocess_data("../data/pizza_dataset/PrevExperimentData.csv")
model = train_model(data)

new_data = {} # to be collected from VR user study (Time & Errors)
cognitive_load = predict(model, new_data)