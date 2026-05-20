from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "10.122.63.179"
PORT = 8080

ultimo_mensaje = "x=0,y=0,z=0"

class SimpleHandler(BaseHTTPRequestHandler):

    def do_POST(self):

        global ultimo_mensaje

        content_length = int(self.headers.get('Content-Length', 0))

        post_data = self.rfile.read(content_length)

        message = post_data.decode("utf-8")

        ultimo_mensaje = message

        print(f"Mensaje recibido: {message}")

        self.send_response(200)

        self.send_header("Content-Type", "text/plain")

        # CORS
        self.send_header("Access-Control-Allow-Origin", "*")

        self.end_headers()

        self.wfile.write(b"Datos recibidos")

    # IMPORTANTE
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

    server = HTTPServer((HOST, PORT), SimpleHandler)

    print(f"Servidor activo en http://10.122.63.179:{PORT}")

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print("\nServidor detenido")

        server.server_close()