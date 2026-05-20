#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

const char* ssid = "wifi";
const char* password = "Gonzalito2014";

const char* serverName = "http://10.122.63.179:8080";

unsigned long lastTime = 0;
unsigned long timerDelay = 200;

void setup() {

  Serial.begin(9600);

  // SDA = 21
  // SCL = 22
  Wire.begin(21, 22);

  if (!mpu.begin()) {

    Serial.println("No se encontró MPU6050");

    while (1) {
      delay(10);
    }
  }

  Serial.println("MPU6050 iniciado");

  WiFi.begin(ssid, password);

  Serial.print("Conectando a ");
  Serial.println(ssid);

  int intentos = 0;

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");

    intentos++;

    if(intentos >= 20){

      Serial.println("\nNo se pudo conectar al WiFi");

      Serial.print("Estado WiFi: ");
      Serial.println(WiFi.status());

      ESP.restart();
    }
  }

  Serial.println("");
  Serial.println("WiFi conectado");

  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());
}

void loop() {

  if ((millis() - lastTime) > timerDelay) {

    if (WiFi.status() == WL_CONNECTED) {

      sensors_event_t a, g, temp;

      mpu.getEvent(&a, &g, &temp);

      float x = a.acceleration.x;
      float y = a.acceleration.y;
      float z = a.acceleration.z;


      Serial.print("X: ");
      Serial.print(x);

      Serial.print(" Y: ");
      Serial.println(y);
      Serial.print(" Z: ");
      Serial.println(z);
      

      WiFiClient client;
      HTTPClient http;

      http.begin(client, serverName);

      http.addHeader("Content-Type", "text/plain");

      String datos = "x=" + String(x) + ",y=" + String(y) + ",z=" + String(z);

      int httpResponseCode = http.POST(datos);

      Serial.print("Código HTTP: ");
      Serial.println(httpResponseCode);

      http.end();

    } else {

      Serial.println("WiFi desconectado");
    }

    lastTime = millis();
  }
}