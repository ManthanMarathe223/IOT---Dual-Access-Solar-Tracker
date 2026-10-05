import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def inspect_data():
    raw_files = [
        "Plant_1_Generation_Data.csv",
        "Plant_1_Weather_Sensor_Data.csv",
        "Plant_2_Generation_Data.csv",
        "Plant_2_Weather_Sensor_Data.csv"
    ]
    
    report = []
    
    for file in raw_files:
        if not os.path.exists(file):
            continue
            
        df = pd.read_csv(file)
        report.append(f"=== File: {file} ===")
        report.append(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
        report.append(f"Columns: {list(df.columns)}")
        report.append(f"Data types:\n{df.dtypes}\n")
        report.append(f"Missing values:\n{df.isnull().sum()}\n")
        report.append(f"Duplicate rows: {df.duplicated().sum()}\n")
        
        if 'PLANT_ID' in df.columns:
            report.append(f"Unique PLANT_ID values: {df['PLANT_ID'].unique()}")
        if 'SOURCE_KEY' in df.columns:
            report.append(f"Unique SOURCE_KEY values ({len(df['SOURCE_KEY'].unique())}): {df['SOURCE_KEY'].unique()[:5]}...")
            
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        report.append("\nSummary statistics (Min, Max, Mean, Median, Std):")
        for col in numerical_cols:
            if col not in ['PLANT_ID']:
                report.append(f"  {col}: Min={df[col].min():.4f}, Max={df[col].max():.4f}, Mean={df[col].mean():.4f}, Median={df[col].median():.4f}, Std={df[col].std():.4f}")
        
        if 'DATE_TIME' in df.columns:
            df['DATE_TIME'] = pd.to_datetime(df['DATE_TIME'])
            report.append(f"\nDate range: {df['DATE_TIME'].min()} to {df['DATE_TIME'].max()}")
            
        report.append("="*50 + "\n")
        
    with open("results/inspection_report.txt", "w") as f:
        f.write("\n".join(report))
        
if __name__ == "__main__":
    inspect_data()
