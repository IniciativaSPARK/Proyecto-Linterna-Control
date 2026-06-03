#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

Adafruit_MPU6050 mpu;

const char* ssid       = "Galaxy S24 FF70";
const char* password   = "Kserola2830";
const char* serverName = "http://10.31.54.179:8080";

unsigned long lastTime   = 0;
unsigned long timerDelay = 20;

WiFiClient client;
HTTPClient http;

//  Guardar últimos valores enviados
float lastX = 0, lastY = 0, lastZ = 0;

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!mpu.begin()) {
    Serial.println("No se encontró MPU6050");
    while (1) delay(10);
  }
  Serial.println("MPU6050 iniciado");

  WiFi.begin(ssid, password);
  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    if (++intentos >= 20) {
      Serial.println("\nNo se pudo conectar");
      ESP.restart();
    }
  }
  Serial.println("\nWiFi conectado: " + WiFi.localIP().toString());
}

void loop() {
  if ((millis() - lastTime) >= timerDelay) {
    lastTime = millis();

    if (WiFi.status() == WL_CONNECTED) {
      sensors_event_t a, g, temp;
      mpu.getEvent(&a, &g, &temp);

      float x = a.acceleration.x;
      float y = a.acceleration.y;
      float z = a.acceleration.z;

      //  Solo enviar si algún eje cambió más de 2 unidades
      if (abs(x - lastX) >= 2.0 || abs(y - lastY) >= 2.0 || abs(z - lastZ) >= 2.0) {

        lastX = x;
        lastY = y;
        lastZ = z;

        String datos = "x=" + String(x, 2) + ",y=" + String(y, 2) + ",z=" + String(z, 2);

        http.begin(client, serverName);
        http.addHeader("Content-Type", "text/plain");

        int httpCode = http.POST(datos);

        if (httpCode < 0) {
          Serial.println("Error HTTP, reconectando...");
          WiFi.reconnect();
        } else {
          Serial.printf("Enviado: %s | HTTP: %d\n", datos.c_str(), httpCode);
        }

        http.end();

      } else {
        Serial.printf("Sin cambio — X:%.2f Y:%.2f Z:%.2f\n", x, y, z);
      }

    } else {
      Serial.println("WiFi desconectado, reconectando...");
      WiFi.reconnect();
      delay(1000);
    }
  }
}
