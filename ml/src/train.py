import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import json

def mean_absolute_percentage_error(y_true, y_pred):
    # Avoid division by zero
    mask = y_true != 0
    if not mask.any():
        return np.nan
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def train_and_evaluate():
    train_df = pd.read_csv('data/normalized/train.csv')
    val_df = pd.read_csv('data/normalized/val.csv')
    test_df = pd.read_csv('data/normalized/test.csv')
    
    features = [
        'AMBIENT_TEMPERATURE', 
        'MODULE_TEMPERATURE', 
        'IRRADIATION',
        'TIME_SIN',
        'TIME_COS',
        'IS_DAY'
    ]
    target = 'AC_POWER'
    
    X_train = train_df[features]
    y_train = train_df[target]
    
    X_test = test_df[features]
    y_test = test_df[target]
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest Regressor': RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1),
        'Gradient Boosting Regressor': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'Extra Trees Regressor': ExtraTreesRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    }
    
    results = []
    best_model = None
    best_r2 = -float('inf')
    best_model_name = ""
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        
        # Predict on Test Set
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test.values, y_pred)
        
        results.append({
            'Model': name,
            'MAE': mae,
            'RMSE': rmse,
            'R2': r2,
            'MAPE': mape
        })
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = model
            best_model_name = name
    
    results_df = pd.DataFrame(results)
    results_df.to_csv('results/metrics.csv', index=False)
    print("\nModel Comparison:\n", results_df)
    
    # Save the best model
    os.makedirs('models/best_model', exist_ok=True)
    joblib.dump(best_model, 'models/best_model/best_model.pkl')
    
    with open('models/best_model/info.json', 'w') as f:
        json.dump({'best_model_name': best_model_name, 'R2': best_r2, 'features': features, 'target': target}, f)
        
    print(f"\nBest model saved: {best_model_name} with R2: {best_r2:.4f}")

if __name__ == "__main__":
    train_and_evaluate()
