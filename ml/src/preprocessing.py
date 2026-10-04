import pandas as pd
import os

def clean_and_merge():
    # Load Plant 1
    p1_gen = pd.read_csv('Plant_1_Generation_Data.csv')
    p1_wea = pd.read_csv('Plant_1_Weather_Sensor_Data.csv')
    
    # Load Plant 2
    p2_gen = pd.read_csv('Plant_2_Generation_Data.csv')
    p2_wea = pd.read_csv('Plant_2_Weather_Sensor_Data.csv')
    
    # Format dates consistently
    p1_gen['DATE_TIME'] = pd.to_datetime(p1_gen['DATE_TIME'], format='%d-%m-%Y %H:%M')
    p1_wea['DATE_TIME'] = pd.to_datetime(p1_wea['DATE_TIME'], format='%Y-%m-%d %H:%M:%S')
    p2_gen['DATE_TIME'] = pd.to_datetime(p2_gen['DATE_TIME'], format='%Y-%m-%d %H:%M:%S')
    p2_wea['DATE_TIME'] = pd.to_datetime(p2_wea['DATE_TIME'], format='%Y-%m-%d %H:%M:%S')
    
    # Drop SOURCE_KEY in weather data as it's just the weather station ID
    p1_wea = p1_wea.drop(columns=['SOURCE_KEY', 'PLANT_ID'])
    p2_wea = p2_wea.drop(columns=['SOURCE_KEY', 'PLANT_ID'])
    
    # Merge on DATE_TIME
    p1_merged = pd.merge(p1_gen, p1_wea, on='DATE_TIME', how='inner')
    p2_merged = pd.merge(p2_gen, p2_wea, on='DATE_TIME', how='inner')
    
    # Combine both plants
    merged_data = pd.concat([p1_merged, p2_merged], ignore_index=True)
    
    # Sort chronologically
    merged_data = merged_data.sort_values(by=['DATE_TIME', 'PLANT_ID', 'SOURCE_KEY'])
    
    # Basic Cleaning: ensure no negative power
    merged_data['DC_POWER'] = merged_data['DC_POWER'].clip(lower=0)
    merged_data['AC_POWER'] = merged_data['AC_POWER'].clip(lower=0)
    
    # Save cleaned data
    merged_data.to_csv('data/cleaned/merged_data.csv', index=False)
    print(f"Cleaned merged data shape: {merged_data.shape}")

if __name__ == "__main__":
    clean_and_merge()
