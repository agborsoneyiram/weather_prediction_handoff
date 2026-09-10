"""
Complete ML Training with Visualizations
FIXED VERSION - Works from any location
"""

import sys
from pathlib import Path

# Fix: Add project root to path (go up 3 levels from this file)
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import config
import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def train_models():
    print("\n" + "="*70)
    print("🤖 TRAINING ML MODELS")
    print("="*70)
    
    # Load data
    data_file = project_root / "data" / "processed" / "features.csv"
    print(f"\n📂 Loading: {data_file}")
    
    if not data_file.exists():
        print(f"❌ File not found: {data_file}")
        print("   Run preprocessing first!")
        return
    
    df = pd.read_csv(data_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    print(f"✅ Loaded {len(df):,} records")
    
    # Split
    n = len(df)
    train_idx = int(n * 0.7)
    val_idx = int(n * 0.8)
    
    train_df = df[:train_idx]
    val_df = df[train_idx:val_idx]
    test_df = df[val_idx:]
    
    print(f"\n📊 Split:")
    print(f"   Train: {len(train_df):,}")
    print(f"   Val:   {len(val_df):,}")
    print(f"   Test:  {len(test_df):,}")
    
    # Features
    exclude = ['timestamp', 'location', 'temp', 'rhum', 'prcp']
    features = [c for c in df.columns if c not in exclude]
    
    print(f"\n🎯 Features: {len(features)}")
    
    all_results = {}
    
    for metric in ['temp', 'rhum', 'prcp']:
        print(f"\n{'='*70}")
        print(f"🎯 TRAINING: {metric.upper()}")
        print(f"{'='*70}")
        
        X_train = train_df[features].values
        y_train = train_df[metric].values
        X_val = val_df[features].values
        y_val = val_df[metric].values
        X_test = test_df[features].values
        y_test = test_df[metric].values
        
        # Scale
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_val = scaler.transform(X_val)
        X_test = scaler.transform(X_test)
        
        # Models
        models = {
            'Random Forest': RandomForestRegressor(
                n_estimators=100, max_depth=20, random_state=42, n_jobs=-1, verbose=0
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100, max_depth=10, random_state=42, verbose=0
            ),
            'Linear Regression': LinearRegression()
        }
        
        results = {}
        
        for name, model in models.items():
            print(f"\n   {name}...", end=" ")
            
            model.fit(X_train, y_train)
            
            val_pred = model.predict(X_val)
            test_pred = model.predict(X_test)
            
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            test_r2 = r2_score(y_test, test_pred)
            
            # Check for overfitting (Linear Regression issue)
            if test_r2 > 0.9999:
                print(f"⚠️ Overfitting detected! (R²={test_r2:.4f})")
                continue
            
            print(f"RMSE: {test_rmse:.4f} | R²: {test_r2:.4f}")
            
            results[name] = {
                'val_rmse': val_rmse,
                'test_rmse': test_rmse,
                'test_r2': test_r2,
                'model': model
            }
        
        # Select best (by validation RMSE)
        if results:
            best_name = min(results.keys(), key=lambda k: results[k]['val_rmse'])
            best = results[best_name]
            
            print(f"\n   ✅ Best: {best_name}")
            
            # Save
            model_path = project_root / "models" / f"rf_{metric}.pkl"
            joblib.dump({
                'model': best['model'],
                'scaler': scaler,
                'features': features
            }, model_path)
            
            print(f"   💾 Saved: {model_path}")
            
            all_results[metric] = results
    
    print(f"\n{'='*70}")
    print("✅ TRAINING COMPLETE!")
    print(f"{'='*70}")

if __name__ == "__main__":
    train_models()