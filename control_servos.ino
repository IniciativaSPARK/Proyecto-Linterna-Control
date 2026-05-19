#include <Servo.h>

Servo servoPan;
Servo servoTilt;

int anguloPan;
int anguloTilt;

void setup() {

  servoPan.attach(3);   // Servo horizontal
  servoTilt.attach(5);  // Servo vertical

  Serial.begin(9600);

  Serial.println("Ingrese dos angulos separados por coma");
  Serial.println("Ejemplo: 90,45");
  // CUIDADO, AL ENVIAR POR SERIAL MONITOR COLOCAR "No Line Ending"
}

void loop() {

  if (Serial.available() > 0) {

    // Leer primer numero
    anguloPan = Serial.parseInt();

    // Leer segundo numero
    anguloTilt = Serial.parseInt();

    // Validar rangos
    if (anguloPan >= 0 && anguloPan <= 180 &&
        anguloTilt >= 0 && anguloTilt <= 180) {

      // Mover servos
      servoPan.write(anguloPan);
      servoTilt.write(anguloTilt);

      // Mostrar datos
      Serial.print("PAN: ");
      Serial.print(anguloPan);

      Serial.print("  TILT: ");
      Serial.println(anguloTilt);

    } else {

      Serial.println("Error: angulos entre 0 y 180");

    }
  }
}
