#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

const char* ssid = "4G-MIFI-CC71";
const char* password = "1234567890";

// Flask server
const char* serverURL = "http://192.168.100.238:5000/sensor-data";

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

    HTTPClient http;

    http.begin(serverURL);

    http.addHeader(
      "Content-Type",
      "application/json"
    );

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

    Serial.println("Sending data to Flask...");

    int httpResponseCode = http.POST(jsonData);

    Serial.print("HTTP response code: ");
    Serial.println(httpResponseCode);

    if (httpResponseCode > 0) {

      String response = http.getString();

      Serial.println("Flask response:");
      Serial.println(response);

    } else {

      Serial.print("Error sending data: ");
      Serial.println(httpResponseCode);

    }

    http.end();

  } else {

    Serial.println("WiFi unavailable. Data not sent.");

  }

  delay(5000);
}

//SENSOR CALIBRATION

// #define RAIN_PIN 34

// void setup() {
//   Serial.begin(115200);

//   delay(1000);

//   Serial.println();
//   Serial.println("========================================");
//   Serial.println("      HW-038 RAIN SENSOR CALIBRATION");
//   Serial.println("========================================");
//   Serial.println();
//   Serial.println("Commands:");
//   Serial.println("D = Dry test");
//   Serial.println("1 = Light wetness test");
//   Serial.println("2 = Moderate wetness test");
//   Serial.println("3 = Heavy wetness test");
//   Serial.println("4 = Very wet test");
//   Serial.println();
//   Serial.println("Each test lasts 30 seconds.");
//   Serial.println("Enter a command to begin.");
//   Serial.println();

//   analogReadResolution(12);
// }

// void runTest(String testName) {

//   Serial.println();
//   Serial.println("========================================");
//   Serial.print("TEST: ");
//   Serial.println(testName);
//   Serial.println("========================================");
//   Serial.println();

//   Serial.println("Starting in 3...");
//   delay(1000);

//   Serial.println("2...");
//   delay(1000);

//   Serial.println("1...");
//   delay(1000);

//   Serial.println("GO!");
//   Serial.println();

//   unsigned long startTime = millis();

//   long total = 0;
//   int count = 0;

//   int minimum = 4095;
//   int maximum = 0;

//   while (millis() - startTime < 30000) {

//     int rainValue = analogRead(RAIN_PIN);

//     total += rainValue;
//     count++;

//     if (rainValue < minimum) {
//       minimum = rainValue;
//     }

//     if (rainValue > maximum) {
//       maximum = rainValue;
//     }

//     Serial.print("Reading: ");
//     Serial.println(rainValue);

//     delay(1000);
//   }

//   float average = (float)total / count;

//   Serial.println();
//   Serial.println("----------------------------------------");
//   Serial.println("TEST COMPLETE");
//   Serial.println("----------------------------------------");

//   Serial.print("Test: ");
//   Serial.println(testName);

//   Serial.print("Samples: ");
//   Serial.println(count);

//   Serial.print("Minimum: ");
//   Serial.println(minimum);

//   Serial.print("Maximum: ");
//   Serial.println(maximum);

//   Serial.print("Average: ");
//   Serial.println(average, 2);

//   Serial.println("----------------------------------------");
//   Serial.println();

//   Serial.println("Enter another command.");
//   Serial.println();
// }

// void loop() {

//   if (Serial.available() > 0) {

//     char command = Serial.read();

//     if (command == 'D' || command == 'd') {
//       runTest("DRY");
//     }

//     else if (command == '1') {
//       runTest("LIGHT");
//     }

//     else if (command == '2') {
//       runTest("MODERATE");
//     }

//     else if (command == '3') {
//       runTest("HEAVY");
//     }

//     else if (command == '4') {
//       runTest("VERY WET");
//     }
//   }
// }