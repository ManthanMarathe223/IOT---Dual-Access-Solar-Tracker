import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
import os

def normalize_data():
    df = pd.read_csv('data/cleaned/featured_data.csv')
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    df = df.sort_values(by=['DATE_TIME', 'PLANT_ID', 'SOURCE_KEY'])
    
    # Chronological Split: 70% Train, 15% Val, 15% Test
    n = len(df)
    train_end = int(n * 0.7)
    val_end = int(n * 0.85)
    
    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]
    
    # Features to normalize
    features_to_normalize = [
        'AMBIENT_TEMPERATURE', 
        'MODULE_TEMPERATURE', 
        'IRRADIATION'
    ]
    
    # We will predict AC_POWER as it represents the usable electrical output.
    # We do NOT use DC_POWER, DAILY_YIELD, TOTAL_YIELD as they would cause data leakage or are redundant.
    
    scaler = MinMaxScaler()
    # Fit ONLY on training data
    scaler.fit(train_df[features_to_normalize])
    
    # Save the scaler
    os.makedirs('models/scaler', exist_ok=True)
    joblib.dump(scaler, 'models/scaler/minmax_scaler.pkl')
    
    # Transform all data using the fitted scaler
    df_normalized = df.copy()
    df_normalized[features_to_normalize] = scaler.transform(df[features_to_normalize])
    
    df_normalized.to_csv('data/normalized/normalized_data.csv', index=False)
    
    # Also save the splits for training
    train_df_norm = df_normalized.iloc[:train_end]
    val_df_norm = df_normalized.iloc[train_end:val_end]
    test_df_norm = df_normalized.iloc[val_end:]
    
    train_df_norm.to_csv('data/normalized/train.csv', index=False)
    val_df_norm.to_csv('data/normalized/val.csv', index=False)
    test_df_norm.to_csv('data/normalized/test.csv', index=False)
    
    print("Normalization complete. Data and scaler saved.")

if __name__ == "__main__":
    normalize_data()
