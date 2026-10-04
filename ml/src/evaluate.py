import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
import json

def generate_plots():
    test_df = pd.read_csv('data/normalized/test.csv')
    df = pd.read_csv('data/cleaned/featured_data.csv')
    
    # Reload info
    with open('models/best_model/info.json', 'r') as f:
        info = json.load(f)
        
    features = info['features']
    target = info['target']
    best_model_name = info['best_model_name']
    
    model = joblib.dump(None, 'models/best_model/dummy') # just to pass linter if needed
    model = joblib.load('models/best_model/best_model.pkl')
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    y_pred = model.predict(X_test)
    
    # 1. Actual vs Predicted Scatter
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.3)
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
    plt.xlabel('Actual AC Power')
    plt.ylabel('Predicted AC Power')
    plt.title(f'Actual vs Predicted AC Power ({best_model_name})')
    plt.tight_layout()
    plt.savefig('results/plots/actual_vs_predicted_scatter.png')
    plt.close()
    
    # 2. Actual vs Predicted over time (first 1000 points for clarity)
    plt.figure(figsize=(15, 6))
    plt.plot(y_test.values[:500], label='Actual', alpha=0.7)
    plt.plot(y_pred[:500], label='Predicted', alpha=0.7)
    plt.xlabel('Time Step')
    plt.ylabel('AC Power')
    plt.title('Actual vs Predicted AC Power Over Time (Sample)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('results/plots/actual_vs_predicted_time.png')
    plt.close()
    
    # 3. Feature Importance
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title("Feature Importances")
        plt.bar(range(X_test.shape[1]), importances[indices], align="center")
        plt.xticks(range(X_test.shape[1]), [features[i] for i in indices], rotation=45)
        plt.xlim([-1, X_test.shape[1]])
        plt.tight_layout()
        plt.savefig('results/plots/feature_importances.png')
        plt.close()
        
    # 4. Irradiation vs Power
    plt.figure(figsize=(10, 6))
    plt.scatter(test_df['IRRADIATION'], y_test, alpha=0.3)
    plt.xlabel('Irradiation (Normalized)')
    plt.ylabel('Actual AC Power')
    plt.title('Irradiation vs Power')
    plt.tight_layout()
    plt.savefig('results/plots/irradiation_vs_power.png')
    plt.close()

if __name__ == "__main__":
    generate_plots()
