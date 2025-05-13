import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import numpy as np

# from sklearn.preprocessing import StandardScaler
# import pandas as pd

# pizza_scaler = StandardScaler()
# pizza_scaled = pizza_scaler.fit_transform(pizza_df[['Time', 'Errors']])
# new_mean = new_df[['Time', 'Errors']].mean()
# new_std = new_df[['Time', 'Errors']].std()
# pizza_mapped = (pizza_scaled * new_std.values) + new_mean.values
# pizza_df_transformed = pd.DataFrame(pizza_mapped, columns=['Time', 'Errors'])

def preprocess_data(file_path):
    df = pd.read_csv(file_path)
    df = df.dropna()
    # task_columns = ['Time1', 'Errors1', 'MWS1', 'Time2', 'Errors2', 'MWS2', 
    #                 'Time3', 'Errors3', 'MWS3', 'Time4', 'Errors4', 'MWS4', 
    #                 'Time5', 'Errors5', 'MWS5']
    reshaped_data = []
    for _, row in df.iterrows():
        for i in range(1, 6):  
            reshaped_data.append({
                'ID': row['ID'],
                'Task': i,
                'Time': row[f'Time{i}'],
                'Errors': row[f'Errors{i}'],
                'MWS': row[f'MWS{i}']
            })
    reshaped_df = pd.DataFrame(reshaped_data)
    # reshaped_df['Time'] = reshaped_df['Time'] / reshaped_df['Time'].max() (no need to normalize since we scaling anyways)
    scaler = StandardScaler()
    reshaped_df[['Time', 'Errors']] = scaler.fit_transform(reshaped_df[['Time', 'Errors']])
    new_mean = [[82.42288223505, 0.2]]
    new_std = [[14.747595618782, 0.2]]
    new_mean = np.array(new_mean).flatten()
    new_std = np.array(new_std).flatten()
    # mapped_data = ( * new_std) + new_mean
    reshaped_df[['Time', 'Errors']] = (reshaped_df[['Time', 'Errors']] * new_std) + new_mean
    joblib.dump(scaler, 'scaler.pkl')  # Save that shii for later when we predict
    reshaped_df['MWS_Label'] = pd.cut(
        reshaped_df['MWS'],
        bins=5, 
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )
    X = reshaped_df[['Time', 'Errors']]
    y = reshaped_df['MWS_Label']  
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "../data/pizza_dataset")
    processed_dir = os.path.join(base_dir, "../data/processed")
    file_path = os.path.join(data_dir, "PrevExperimentData.csv")
    X_train, X_test, y_train, y_test = preprocess_data(file_path)
    os.makedirs(processed_dir, exist_ok=True)
    X_train.to_csv(os.path.join(processed_dir, "X_train.csv"), index=False)
    X_test.to_csv(os.path.join(processed_dir, "X_test.csv"), index=False)
    y_train.to_csv(os.path.join(processed_dir, "y_train.csv"), index=False)
    y_test.to_csv(os.path.join(processed_dir, "y_test.csv"), index=False)
    print("Preprocessing done homie, send this data over to train.")