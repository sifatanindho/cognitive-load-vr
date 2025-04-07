import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preprocess_data(file_path):
    df = pd.read_csv(file_path)

    df = df.dropna()

    task_columns = ['Time1', 'Errors1', 'MWS1', 'Time2', 'Errors2', 'MWS2', 
                        'Time3', 'Errors3', 'MWS3', 'Time4', 'Errors4', 'MWS4', 
                        'Time5', 'Errors5', 'MWS5']

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

    # Normalize time
    reshaped_df['Time'] = reshaped_df['Time'] / reshaped_df['Time'].max()

    # Scale time and errors to standardize (mean 0 and variance 1)
    scaler = StandardScaler()
    reshaped_df[['Time', 'Errors']] = scaler.fit_transform(reshaped_df[['Time', 'Errors']])

    # Split the data into features (X) and target (y)
    X = reshaped_df[['Time', 'Errors']]
    y = reshaped_df['MWS']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    file_path = '../data/pizza_dataset/PrevExperimentData.csv'
    X_train, X_test, y_train, y_test = preprocess_data(file_path)
    # Save the preprocessed data to CSV files
    X_train.to_csv('../data/processed/X_train.csv', index=False)
    X_test.to_csv('../data/processed/X_test.csv', index=False)
    y_train.to_csv('../data/processed/y_train.csv', index=False)
    y_test.to_csv('../data/processed/y_test.csv', index=False)
    
    print("Preprocessing complete. Training and testing data are ready.")
