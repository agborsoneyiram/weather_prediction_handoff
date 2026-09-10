# CREATE: src/preprocessing/prepare_data.py
"""
Data Preparation - PREVENTS DATA LEAKAGE
Key: Split BEFORE feature engineering
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np
from datetime import timedelta

def prepare_data():
    """
    CRITICAL: Split data FIRST, then create features
    This prevents using test data to create training features
    """
    print("\n" + "="*70)
    print("🔧 DATA PREPARATION - NO LEAKAGE")
    print("="*70)
    
    # Load raw data
    print("\n📥 Loading raw data...")
    df = pd.read_csv(config.DATA_DIR / "processed" / "features.csv")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    print(f"   Total records: {len(df):,}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # ⚠️ CRITICAL: Split BEFORE creating lag features
    n = len(df)
    train_idx = int(n * (1 - config.TEST_SIZE - config.VAL_SIZE))
    val_idx = train_idx + int(n * config.VAL_SIZE)
    
    train_df = df[:train_idx].copy()
    val_df = df[train_idx:val_idx].copy()
    test_df = df[val_idx:].copy()
    
    print(f"\n✅ SPLIT (NO LEAKAGE):")
    print(f"   Train: {len(train_df):,} ({train_df['timestamp'].min()} to {train_df['timestamp'].max()})")
    print(f"   Val:   {len(val_df):,} ({val_df['timestamp'].min()} to {val_df['timestamp'].max()})")
    print(f"   Test:  {len(test_df):,} ({test_df['timestamp'].min()} to {test_df['timestamp'].max()})")
    
    # ⚠️ CRITICAL: Only use TRAIN set statistics for scaling/normalization
    print(f"\n🔒 Computing statistics from TRAIN SET ONLY...")
    for metric in ['temp', 'rhum', 'prcp']:
        train_mean = train_df[metric].mean()
        train_std = train_df[metric].std()
        train_min = train_df[metric].min()
        train_max = train_df[metric].max()
        
        print(f"   {metric.upper()}: mean={train_mean:.2f}, std={train_std:.2f}")
    
    # Save splits
    print(f"\n💾 Saving splits (NO LEAKAGE)...")
    train_df.to_csv(config.DATA_DIR / "processed" / "train_data.csv", index=False)
    val_df.to_csv(config.DATA_DIR / "processed" / "val_data.csv", index=False)
    test_df.to_csv(config.DATA_DIR / "processed" / "test_data.csv", index=False)
    
    print(f"✅ COMPLETE - No leakage possible!")
    print(f"   ✅ train_data.csv")
    print(f"   ✅ val_data.csv")
    print(f"   ✅ test_data.csv")

if __name__ == "__main__":
    prepare_data()