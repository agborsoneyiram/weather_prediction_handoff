"""Weather Prediction - Kasoa+Accra - Config"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

for d in [
    DATA_DIR,
    MODELS_DIR,
    OUTPUTS_DIR,
    DATA_DIR / "historical",
    DATA_DIR / "realtime",
    DATA_DIR / "processed",
    DATA_DIR / "arduino"
]:
    d.mkdir(parents=True, exist_ok=True)

TARGET_METRICS = ['temp', 'rhum', 'prcp']
MODEL_FILES = {
    "temp": "temp_model.pkl",
    "rhum": "rhum_model.pkl",
    "prcp": "prcp_model.pkl"
}

LOCATIONS = {
    'kasoa': {'name': 'Kasoa', 'lat': 5.5333, 'lon': -0.4167},
    'accra': {'name': 'Accra', 'lat': 5.6037, 'lon': -0.1870}
}

OPEN_METEO_API = 'https://archive-api.open-meteo.com/v1/archive'
OPEN_METEO_REALTIME = 'https://api.open-meteo.com/v1/forecast'

START_DATE = "2020-01-01"
END_DATE = "2026-06-15"
LAG_HOURS = [1, 3, 6, 12, 24]
ROLLING_WINDOWS = [6, 12, 24]

RANDOM_SEED = 42
# ============ TRAINING SPLITS ============
TRAIN_START_DATE = "2020-01-01"
TRAIN_END_DATE = "2025-12-31"

VALIDATION_START_DATE = "2026-01-01"
VALIDATION_END_DATE = "2026-03-19"

BACKTEST_TEST_START = "2026-04-01"
BACKTEST_TEST_END = "2026-06-15"

PREDICTION_HORIZONS = [1, 7]

VALIDATION_DIR = PROJECT_ROOT / "validation_results"
VALIDATION_DIR.mkdir(parents=True, exist_ok=True)

print("✅ Kasoa+Accra | Temp+Humidity+Rainfall | Open-Meteo | XGBoost")

# ============ RAIN SENSOR CALIBRATION ============
RAIN_THRESHOLDS = {
    "dry": 75,
    "light": 217,
    "moderate": 442,
    "heavy": 961
}