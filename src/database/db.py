import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "weather_prediction")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


def test_connection():
    """Test the MySQL database connection."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("✅ MySQL database connected successfully")
        return True

    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False


def save_sensor_reading(reading):
    """Save one ESP32 sensor reading to MySQL."""

    query = text("""
        INSERT INTO sensor_readings
        (timestamp, temperature, humidity, rain_value, rain_status, source, device_id, location)
        VALUES
        (:timestamp, :temperature, :humidity, :rain_value, :rain_status, :source, :device_id, :location)
    """)

    try:
        with engine.begin() as connection:
            connection.execute(
                query,
                {
                    "timestamp": reading["timestamp"],
                    "temperature": reading["temperature"],
                    "humidity": reading["humidity"],
                    "rain_value": reading["rain_value"],
                    "rain_status": reading["rain_status"],
                    "source": reading["source"],
                    "device_id": reading["device_id"],
                    "location": reading["location"]
                }
            )

        return True

    except Exception as e:
        print(f"❌ Failed to save sensor reading: {e}")
        raise

def get_sensor_history(hours=24):
    """Get recent ESP32 sensor readings from MySQL."""

    query = text("""
        SELECT
            timestamp,
            temperature,
            humidity,
            rain_value,
            rain_status,
            source
        FROM sensor_readings
        WHERE timestamp >= NOW() - INTERVAL :hours HOUR
        ORDER BY timestamp ASC
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(
                query,
                {"hours": hours}
            )

            rows = result.mappings().all()

        return [dict(row) for row in rows]

    except Exception as e:
        print(f"❌ Failed to retrieve sensor history: {e}")
        return []

def get_latest_sensor_reading():
    """Get the most recent ESP32 sensor reading from MySQL."""

    query = text("""
        SELECT
            id,
            timestamp,
            temperature,
            humidity,
            rain_value,
            rain_status,
            source
        FROM sensor_readings
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().first()

        if result is None:
            return None

        return dict(result)

    except Exception as e:
        print(f"❌ Failed to retrieve latest sensor reading: {e}")
        return None

    if __name__ == "__main__":
        test_connection()

    print("✅ MySQL database connected successfully")