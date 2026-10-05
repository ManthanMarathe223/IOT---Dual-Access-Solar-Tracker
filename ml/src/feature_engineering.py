import pandas as pd
import numpy as np

def engineer_features():
    df = pd.read_csv('data/cleaned/merged_data.csv')
    df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
    
    # Time features
    df['HOUR'] = df['DATE_TIME'].dt.hour
    df['MINUTE'] = df['DATE_TIME'].dt.minute
    df['TIME_IN_MINUTES'] = df['HOUR'] * 60 + df['MINUTE']
    df['DAY_OF_YEAR'] = df['DATE_TIME'].dt.dayofyear
    
    # Cyclic encoding for time
    df['TIME_SIN'] = np.sin(2 * np.pi * df['TIME_IN_MINUTES'] / 1440)
    df['TIME_COS'] = np.cos(2 * np.pi * df['TIME_IN_MINUTES'] / 1440)
    
    # Day/Night indicator (very simple assumption based on irradiation or typical solar hours)
    # Using Irradiation > 0.0 as Day
    df['IS_DAY'] = (df['IRRADIATION'] > 0.0).astype(int)
    
    # Drop rows with NaN if any
    df = df.dropna()
    
    # Drop string/ID columns for ML input, keep them in another frame or save index
    # We will just save everything and handle selection during training.
    df.to_csv('data/cleaned/featured_data.csv', index=False)
    print(f"Featured data shape: {df.shape}")

if __name__ == "__main__":
    engineer_features()
