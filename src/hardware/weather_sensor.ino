#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>

const char* ssid = "S25Ultra";
const char* password = "yawa1234";

// Railway Flask server
const char* serverURL = "https://weatherpredictionhandoff-production.up.railway.app/sensor-data";

// Device information
const char* deviceId = "ESP32_001";
const char* location = "Kasoa";

// Sensors
#define DHTPIN 4
#define DHTTYPE DHT11
#define RAIN_PIN 34

DHT dht(DHTPIN, DHTTYPE);

void connectWiFi() {

  Serial.print("Connecting to WiFi");

  WiFi.begin(ssid, password);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 20) {

    delay(500);
    Serial.print(".");

    attempts++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println("WiFi connected!");

    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());

  } else {

    Serial.println("WiFi connection failed.");

  }
}

void setup() {

  Serial.begin(115200);

  dht.begin();

  Serial.println();
  Serial.println("================================");
  Serial.println("   WEATHER SENSOR SYSTEM");
  Serial.println("================================");

  connectWiFi();

  Serial.println("Sensors ready!");
}

void loop() {

  // Reconnect if Wi-Fi has been lost
  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi disconnected.");
    connectWiFi();

  }

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int rainValue = analogRead(RAIN_PIN);

  if (isnan(temperature) || isnan(humidity)) {

    Serial.println("DHT11 reading failed!");

    delay(5000);
    return;
  }

  Serial.println();
  Serial.println("----------------------------");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Rain sensor: ");
  Serial.println(rainValue);

  if (WiFi.status() == WL_CONNECTED) {

    WiFiClientSecure client;

    // For testing/demo purposes
    client.setInsecure();

    HTTPClient http;

    if (http.begin(client, serverURL)) {

      http.addHeader("Content-Type", "application/json");

      String jsonData = "{";

      jsonData +=
        "\"temperature\":" +
        String(temperature, 1);

      jsonData +=
        ",\"humidity\":" +
        String(humidity, 1);

      jsonData +=
        ",\"rain_value\":" +
        String(rainValue);

      jsonData +=
        ",\"device_id\":\"" +
        String(deviceId) +
        "\"";

      jsonData +=
        ",\"location\":\"" +
        String(location) +
        "\"";

      jsonData += "}";

      Serial.println("Sending data to Railway...");
      Serial.println(jsonData);

      int httpResponseCode = http.POST(jsonData);

      Serial.print("HTTP response code: ");
      Serial.println(httpResponseCode);

      if (httpResponseCode > 0) {

        String response = http.getString();

        Serial.println("Railway response:");
        Serial.println(response);

      } else {

        Serial.print("Error sending data: ");
        Serial.println(httpResponseCode);

      }

      http.end();

    } else {

      Serial.println("Failed to connect to Railway server.");

    }

  } else {

    Serial.println("WiFi unavailable. Data not sent.");

  }

  delay(5000);
}