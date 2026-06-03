from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from datetime import datetime
import serial
import serial.tools.list_ports
import re
import sys

# =========================
# CONFIGURACIÓN
# =========================
HOST = "0.0.0.0"
PORT = 8080
BAUDRATE = 115200

ultimo_mensaje = "x=0,y=0,z=0"
arduino = None

# =========================
# REGEX
# =========================
PATRON_MENSAJE = re.compile(
    r"^x=(-?\d+(?:\.\d+)?),y=(-?\d+(?:\.\d+)?),z=(-?\d+(?:\.\d+)?)$"
)

# =========================
# CONECTAR ARDUINO
# =========================
def conectar_arduino():
    global arduino

    puertos = serial.tools.list_ports.comports()

    print("\nPuertos detectados:")

    for puerto in puertos:
        print(f"- {puerto.device} | {puerto.description}")

    for puerto in puertos:

        descripcion = puerto.description.lower()

        if (
            "arduino" in descripcion
            or "ch340" in descripcion
            or "usb serial" in descripcion
            or "dispositivo serie usb" in descripcion
        ):

            try:

                arduino = serial.Serial(
                    port=puerto.device,
                    baudrate=BAUDRATE,
                    timeout=0.1
                )

                print(f"\nArduino conectado en {puerto.device}")

                return True

            except Exception as e:

                print(f"Error al conectar Arduino: {e}")

    return False


# =========================
# VALIDAR MENSAJE
# =========================
def validar_mensaje(message):

    resultado = PATRON_MENSAJE.match(message)

    if resultado:

        x = float(resultado.group(1))
        y = float(resultado.group(2))
        z = float(resultado.group(3))

        return True, x, y, z

    return False, None, None, None


# =========================
# SERVIDOR MULTIHILO
# =========================
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


# =========================
# HANDLER HTTP
# =========================
class SimpleHandler(BaseHTTPRequestHandler):

    def enviar_headers(self, codigo):

        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    # =========================
    # OPTIONS (CORS)
    # =========================
    def do_OPTIONS(self):

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()

    # =========================
    # POST
    # =========================
    def do_POST(self):

        global ultimo_mensaje
        global arduino

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        post_data = self.rfile.read(content_length)

        message = post_data.decode(
            "utf-8"
        ).strip()

        valido, x, y, z = validar_mensaje(message)

        if not valido:

            self.enviar_headers(400)

            self.wfile.write(
                b"Formato invalido. Use: x=1,y=2,z=3"
            )

            print(
                f"Formato invalido: {message}"
            )

            return

        ultimo_mensaje = message

        # =========================
        # MPU6050 -> SERVO
        # =========================
        servo_x = round(
            90 + (x * 9)
        )

        servo_y = round(
            90 + (y * 9)
        )

        servo_x = max(
            0,
            min(180, servo_x)
        )

        servo_y = max(
            0,
            min(180, servo_y)
        )

        # =========================
        # ENVIAR A ARDUINO
        # =========================
        if arduino and arduino.is_open:

            mensaje_serial = (
                f"{servo_x},{servo_y}\n"
            )

            try:

                arduino.write(
                    mensaje_serial.encode()
                )

                hora = datetime.now().strftime(
                    "%H:%M:%S.%f"
                )[:-3]

                print(
                    f"\n[{hora}] RECIBIDO"
                )

                print(
                    f"X={x:7.2f} | "
                    f"Y={y:7.2f} | "
                    f"Z={z:7.2f}"
                )

                print(
                    f"[{hora}] ENVIADO"
                )

                print(
                    f"ServoX={servo_x:3}° | "
                    f"ServoY={servo_y:3}°"
                )

                print(
                    "------------------------------------"
                )

            except Exception as e:

                print(
                    f"Error enviando al Arduino: {e}"
                )

        else:

            print(
                "Arduino no conectado"
            )

        self.enviar_headers(200)

        self.wfile.write(b"OK")

    # =========================
    # GET
    # =========================
    def do_GET(self):

        global ultimo_mensaje

        self.enviar_headers(200)

        self.wfile.write(
            ultimo_mensaje.encode()
        )

    # Ocultar logs HTTP
    def log_message(self, format, *args):
        return


# =========================
# MAIN
# =========================
if __name__ == "__main__":

    print("===================================")
    print("   BUSCANDO ARDUINO UNO")
    print("===================================")

    if not conectar_arduino():

        print(
            "No se encontró un Arduino conectado"
        )

        sys.exit()

    server = ThreadedHTTPServer(
        (HOST, PORT),
        SimpleHandler
    )

    print(
        f"\nServidor activo en http://{HOST}:{PORT}"
    )

    print(
        "Esperando datos...\n"
    )

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nServidor detenido"
        )

    finally:

        if arduino and arduino.is_open:
            arduino.close()

        server.server_close()

        print(
            "Recursos liberados correctamente"
        )