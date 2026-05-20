from http.server import BaseHTTPRequestHandler, HTTPServer
import serial
import serial.tools.list_ports
import re
import sys

HOST = "0.0.0.0"
PORT = 8080

ultimo_mensaje = "x=0,y=0,z=0"

# =========================
# CONFIGURACION SERIAL
# =========================
BAUDRATE = 9600
arduino = None

def conectar_arduino():

    global arduino

    puertos = serial.tools.list_ports.comports()

    print("Puertos detectados:")

    for puerto in puertos:

        print(f"- {puerto.device} | {puerto.description}")

    for puerto in puertos:

        descripcion = puerto.description.lower()

        # Detectar Arduino UNO
        if (
            "arduino" in descripcion or
            "ch340" in descripcion or
            "usb serial" in descripcion or
            "dispositivo serie usb" in descripcion
        ):

            try:

                arduino = serial.Serial(
                    port=puerto.device,
                    baudrate=BAUDRATE,
                    timeout=1
                )

                print(f"Arduino conectado en {puerto.device}")

                return True

            except Exception as e:

                print(f"Error al conectar con Arduino: {e}")

    return False

# =========================
# VALIDACION DE MENSAJE
# =========================
# =========================
# VALIDACION DE MENSAJE
# =========================
def validar_mensaje(message):
    """
    Valida formato:
    x=12.5,y=20,z=-7.8

    x y z aceptan enteros o decimales.
    Luego se redondean a enteros.
    """

    patron = r"^x=(-?\d+(?:\.\d+)?),y=(-?\d+(?:\.\d+)?),z=(-?\d+(?:\.\d+)?)$"

    resultado = re.match(patron, message)

    if resultado:

        # Convertir a float y redondear
        x = round(float(resultado.group(1)))
        y = round(float(resultado.group(2)))
        z = round(float(resultado.group(3)))

        return True, x, y, z

    return False, None, None, None

class SimpleHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        global ultimo_mensaje
        global arduino

        content_length = int(self.headers.get('Content-Length', 0))

        post_data = self.rfile.read(content_length)

        message = post_data.decode("utf-8").strip()

        print(f"Mensaje recibido: {message}")

        # =========================
        # VALIDAR FORMATO
        # =========================
        valido, x, y, z = validar_mensaje(message)

        if not valido:

            self.send_response(400)

            self.send_header("Content-Type", "text/plain")

            # CORS
            self.send_header("Access-Control-Allow-Origin", "*")

            self.end_headers()

            self.wfile.write(
                b"Formato invalido. Use: x=1,y=2,z=3"
            )

            print("Formato inválido")

            return

        # Guardar mensaje válido
        ultimo_mensaje = message

        # =========================
        # ENVIAR A ARDUINO
        # =========================
        if arduino and arduino.is_open:

            x = x/10*180
            y = y/10*180
            mensaje_serial = f"{x},{y}\n"

            try:
                arduino.write(mensaje_serial.encode())

                print(f"Enviado al Arduino: {mensaje_serial.strip()}")

            except Exception as e:
                print(f"Error enviando al Arduino: {e}")

        else:
            print("Arduino no conectado")

        # =========================
        # RESPUESTA HTTP
        # =========================
        self.send_response(200)

        self.send_header("Content-Type", "text/plain")

        # CORS
        self.send_header("Access-Control-Allow-Origin", "*")

        self.end_headers()

        self.wfile.write(b"Datos recibidos correctamente")

    # =========================
    # GET
    # =========================
    def do_GET(self):

        global ultimo_mensaje

        print("Enviando:", ultimo_mensaje)

        self.send_response(200)

        self.send_header("Content-Type", "text/plain")

        # CORS
        self.send_header("Access-Control-Allow-Origin", "*")

        self.end_headers()

        self.wfile.write(ultimo_mensaje.encode())

    def log_message(self, format, *args):
        return


if __name__ == "__main__":

    # =========================
    # VALIDAR CONEXION ARDUINO
    # =========================
    print("Buscando Arduino UNO...")

    if not conectar_arduino():

        print("No se encontró un Arduino conectado")
        sys.exit()

    # =========================
    # INICIAR SERVIDOR
    # =========================
    server = HTTPServer((HOST, PORT), SimpleHandler)

    print(f"Servidor activo en http://{HOST}:{PORT}")

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print("\nServidor detenido")

        if arduino and arduino.is_open:
            arduino.close()

        server.server_close()


# HASTA ACA FUNCIONA TODO EUREKAAAA