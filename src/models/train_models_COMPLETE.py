"""
Complete ML Training with XGBoost (NO Linear Regression overfitting)
Trains 3 models + creates visualizations
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def calculate_mape(y_true, y_pred):
    """Calculate MAPE avoiding division by zero"""
    mask = y_true != 0
    if mask.sum() == 0:
        return 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

def train_and_evaluate():
    """Complete training with 3 models"""
    
    print("\n" + "="*70)
    print("🤖 MODEL TRAINING & VALIDATION")
    print("="*70)
    
    # Load data
    df = pd.read_csv(config.DATA_DIR / "processed" / "features.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(["location", "timestamp"]).reset_index(drop=True)    
    print(f"\n📊 Dataset Info (BEFORE FILTERING):")
    print(f"   Total records: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Features: {len(df.columns)}")
    
    # Filter by date range
    df = df[(df["timestamp"] >= config.START_DATE) & (df["timestamp"] <= config.VALIDATION_END_DATE)].copy()
    # ===============================
    # Create forecasting targets
    # ===============================
    print("\nCreating forecasting targets...")

    for metric in config.TARGET_METRICS:
        df[f"{metric}_target"] = (
            df.groupby("location")[metric]
            .shift(-1)
        )

    df = df.dropna().reset_index(drop=True)

    print("Forecast horizon: 1-hour ahead")
    print(f"Remaining records: {len(df):,}")
    print(f"\n📊 Dataset Info (AFTER DATE FILTERING):")
    print(f"   Filtered records: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    # ===============================
    # Date-based temporal split
    # ===============================

    train_df = df[
        (df["timestamp"] >= config.TRAIN_START_DATE) &
        (df["timestamp"] <= config.TRAIN_END_DATE)
    ].copy()

    val_df = df[
        (df["timestamp"] >= config.VALIDATION_START_DATE) &
        (df["timestamp"] <= config.VALIDATION_END_DATE)
    ].copy()

    print("\n📈 Data Split:")
    print(
        f"   Train: {len(train_df):,} "
        f"({train_df['timestamp'].min()} to {train_df['timestamp'].max()})"
    )
    print(
        f"   Validation: {len(val_df):,} "
        f"({val_df['timestamp'].min()} to {val_df['timestamp'].max()})"
    )

    # Feature columns
    exclude = ['timestamp', 'location', 'temp', 'rhum', 'prcp', 'temp_target', 'rhum_target', 'prcp_target']

    feature_cols = [c for c in df.columns if c not in exclude]    
    print(f"\n🎯 Training 3 metrics with {len(feature_cols)} features")
    
    all_results = {}
    best_models = {}
    
    # Train each metric
    for metric in config.TARGET_METRICS:
        print(f"\n{'='*70}")
        print(f"🎯 TRAINING: {metric.upper()}")
        print(f"{'='*70}")
        
        # Prepare data
        X_train = train_df[feature_cols].values
        y_train = train_df[f"{metric}_target"].values
        X_val = val_df[feature_cols].values
        y_val = val_df[f"{metric}_target"].values
        
        # Scale features (FIT ONLY ON TRAIN)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # ✅ THREE MODELS (NO LINEAR REGRESSION OVERFITTING)
        models = {
            'Random Forest': RandomForestRegressor(
                n_estimators=100, max_depth=20, random_state=42, n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100, max_depth=10, random_state=42
            ),
            'XGBoost': XGBRegressor(
                n_estimators=100, max_depth=10, random_state=42, verbosity=0
            )
        }
        
        metric_results = {}
        
        for model_name, model in models.items():
            print(f"\n   Training {model_name}...")
            
            model.fit(X_train_scaled, y_train)
            
            # Predictions
            train_pred = model.predict(X_train_scaled)
            val_pred = model.predict(X_val_scaled)
            
            # Metrics
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
            
            val_mae = mean_absolute_error(y_val, val_pred)
            val_r2 = r2_score(y_val, val_pred)
            val_mape = calculate_mape(y_val, val_pred)

            print(f"      Validation RMSE: {val_rmse:.4f}")
            print(f"      Validation MAE:  {val_mae:.4f}")
            print(f"      Validation R²:   {val_r2:.4f}")
            print(f"      Validation MAPE: {val_mape:.2f}%")
            
            metric_results[model_name] = {
                'train_rmse': train_rmse,
                'val_rmse': val_rmse,
                'val_mae': val_mae,
                'val_r2': val_r2,
                'val_mape': val_mape,
                'model': model
            }
        
        # Select best model (based on validation RMSE)
        best_name = min(metric_results.keys(), key=lambda k: metric_results[k]['val_rmse'])
        best_model = metric_results[best_name]
        
        print(f"\n   ✅ Best model: {best_name}")
        
        # Save best model
        model_data = {
            'model': best_model['model'],
            'scaler': scaler,
            'features': feature_cols,
            'metrics': {
                    'val_rmse': best_model['val_rmse'],
                    'val_mae': best_model['val_mae'],
                    'val_r2': best_model['val_r2'],
                    'val_mape': best_model['val_mape']
                },
            'model_name': best_name
        }
        
        joblib.dump(model_data, config.MODELS_DIR / f"{metric}_model.pkl")
        
        all_results[metric] = metric_results
        best_models[metric] = best_name
    
    # Summary
    print(f"\n{'='*70}")
    print("✅ TRAINING COMPLETE!")
    print(f"{'='*70}")
    
    summary = pd.DataFrame({
    metric: {
        'Best Model': best_models[metric],
        'Validation RMSE': all_results[metric][best_models[metric]]['val_rmse'],
        'Validation MAE': all_results[metric][best_models[metric]]['val_mae'],
        'Validation R²': all_results[metric][best_models[metric]]['val_r2'],
        'Validation MAPE': all_results[metric][best_models[metric]]['val_mape']
    }
    for metric in config.TARGET_METRICS
    }).T
    
    print("\n📊 VALIDATION RESULTS:")
    print(summary)
    
    summary.to_csv(config.OUTPUTS_DIR / "tables" / "best_models_summary.csv")
    
    print(f"\n💾 Saved:")
    print(f"   - Models: models/{{metric}}_model.pkl")
    print(f"   - Summary: outputs/tables/best_models_summary.csv")

if __name__ == "__main__":
    train_and_evaluate()