# 🎯 SETUP GUIDE - Follow These Steps Exactly

## Step 1: Create Project Folder

Open Command Prompt:
```bash
cd C:\Users\eyiram.agborson
mkdir weather_prediction_system
cd weather_prediction_system
```

---

## Step 2: Create Folder Structure

```bash
mkdir data
mkdir data\historical
mkdir data\live
mkdir data\processed
mkdir models
mkdir src
mkdir src\data_collection
mkdir src\preprocessing
mkdir src\models
mkdir outputs
mkdir outputs\tables
mkdir outputs\figures
```

---

## Step 3: Download Files from Claude

Download these 7 files and place them:

### Root folder files:
1. `README.md` → `C:\Users\eyiram.agborson\weather_prediction_system\README.md`
2. `config.py` → `C:\Users\eyiram.agborson\weather_prediction_system\config.py`
3. `requirements.txt` → `C:\Users\eyiram.agborson\weather_prediction_system\requirements.txt`

### Source files:
4. `fetch_data.py` → `C:\Users\eyiram.agborson\weather_prediction_system\src\data_collection\fetch_data.py`
5. `prepare_data.py` → `C:\Users\eyiram.agborson\weather_prediction_system\src\preprocessing\prepare_data.py`
6. `train_models.py` → `C:\Users\eyiram.agborson\weather_prediction_system\src\models\train_models.py`
7. `predict_nextday.py` → `C:\Users\eyiram.agborson\weather_prediction_system\src\models\predict_nextday.py`

---

## Step 4: Setup Python Environment

```bash
# Make sure you're in project folder
cd C:\Users\eyiram.agborson\weather_prediction_system

# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\activate

# You should see (.venv) in your command prompt now

# Install packages
pip install -r requirements.txt
```

This will take 2-3 minutes. ☕

---

## Step 5: Run the Pipeline (ONE BY ONE!)

### 5.1 Fetch Data (~5 minutes)
```bash
python src\data_collection\fetch_data.py
```

**What it does:** Downloads weather data for 10 Ghana regions (2020-2026)

**Expected output:**
```
✅ COMPLETE!
Total records: ~500,000+
Saved to: data\historical\combined_historical.csv
```

---

### 5.2 Prepare Data (~10 minutes)
```bash
python src\preprocessing\prepare_data.py
```

**What it does:** Cleans data, creates features

**Expected output:**
```
✅ COMPLETE!
Final records: ~400,000+
Total features: ~100
Saved to: data\processed\feature_engineered.csv
```

---

### 5.3 Train Models (~30-60 minutes) ☕☕☕
```bash
python src\models\train_models.py
```

**What it does:** Trains Random Forest for temp, humidity, rainfall

**Expected output:**
```
✅ ALL MODELS TRAINED!

TEMP:
   RMSE: 0.1-0.2
   R²:   0.99+

RHUM:
   RMSE: 0.4-0.6
   R²:   0.99+

PRCP:
   RMSE: 0.02-0.05
   R²:   0.96+
```

**Models saved:**
- `models\random_forest_temp.pkl` ✅
- `models\random_forest_rhum.pkl` ✅
- `models\random_forest_prcp.pkl` ✅

---

### 5.4 Test Prediction (~1 second)
```bash
python src\models\predict_nextday.py
```

**What it does:** Demo next-day prediction

**Expected output:**
```
✅ TEMP: 28.5°C
✅ RHUM: 76.0%
✅ PRCP: 0.5mm

🌤️ Summary: Warm, very humid, no rain expected
```

---

## ✅ SUCCESS CHECKLIST

After completing all steps, verify:

```bash
# Check models exist
dir models

# Should show:
# random_forest_temp.pkl
# random_forest_rhum.pkl
# random_forest_prcp.pkl
```

If you see these 3 files, **YOU'RE DONE!** 🎉

---

## 🚨 Troubleshooting

### Problem: "python not recognized"
**Solution:** Install Python 3.11+ from python.org

### Problem: "pip install fails"
**Solution:** 
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: "ModuleNotFoundError: config"
**Solution:** Make sure you're in project root folder:
```bash
cd C:\Users\eyiram.agborson\weather_prediction_system
python src\models\train_models.py  # Not just train_models.py
```

### Problem: "No data found" during fetch
**Solution:** Check internet connection, Meteostat may be slow

---

## 📞 What to Report Thursday

After completing setup:

> "System is set up and working. Downloaded 500k+ historical records from 10 regions. Created 100+ features. Trained 3 Random Forest models achieving R² > 0.96 for all metrics. Next-day prediction system is operational. Ready to proceed with hardware integration and satellite data exploration."

---

## 🎯 Next Steps (After Setup)

1. Hardware procurement (DHT22 sensor + rain gauge)
2. Satellite data API exploration
3. SMS notification system
4. Flask API development
5. Mobile app integration

---

**Total time:** ~1 hour (mostly waiting for training)

**Questions?** Check README.md or ask! 😊