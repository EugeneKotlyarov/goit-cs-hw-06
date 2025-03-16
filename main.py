import socket
import threading
import json
from datetime import datetime as dt
from http.server import BaseHTTPRequestHandler, HTTPServer
from pymongo import MongoClient
from urllib.parse import parse_qs

# порти
PORT_H = 3000
PORT_S = 5000

# MONGO PART
DB_URI = f"mongodb://admin111:admin111@mongo/?retryWrites=true&w=majority"
DB_NAME = "msg_db"
CLCT_NAME = "messages"
client = MongoClient(DB_URI)
db = client[DB_NAME]
collection = db[CLCT_NAME]


# SOCKET SERVER PART
def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", PORT_S))
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()
        data = client_socket.recv(1024)
        if data:
            try:
                # обробка і відправка у монго
                received_json = data.decode("utf-8")
                message_data = json.loads(received_json)
                message_data["date"] = str(dt.now())
                collection.insert_one(message_data)
            except Exception as e:
                print(f"Socket error: {e}")
        client_socket.close()


# HTTP SERVER PART
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        match self.path:
            case "/" | "/index.html":
                self.serve_file("index.html")
            case "/message.html":
                self.serve_file("message.html")
            case path if path.endswith(".css"):
                self.serve_file("style.css")
            case path if path.endswith(".png"):
                self.serve_file("logo.png")
            case _:
                self.send_error(404, "Page not found")
                self.serve_file("error.html")

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            parsed_data = parse_qs(post_data.decode("utf-8"))
            username = parsed_data.get("username", ["Anonymous"])[0]
            message = parsed_data.get("message", [""])[0]
            socket_data = json.dumps({"username": username, "message": message})
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(("localhost", PORT_S))
                sock.sendall(socket_data.encode("utf-8"))

            self.send_response(302)
            self.send_header("Location", "/message.html")
            self.end_headers()
        else:
            self.send_error(404, "Page not found")
            self.serve_file("error.html")

    def serve_file(self, file_path, status_code=200):
        try:
            with open(file_path, "rb") as file:
                self.send_response(status_code)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, "Page not found")

    def serve_static_file(self, file_path):
        """Serve static files (CSS, images, etc.)."""
        try:
            match file_path:
                case path if path.endswith(".css"):
                    content_type = "text/css"
                case path if path.endswith(".png"):
                    content_type = "image/png"
                case path if path.endswith(".jpg") | path.endswith(".jpeg"):
                    content_type = "image/jpeg"
                case path if path.endswith(".js"):
                    content_type = "application/javascript"
                case _:
                    content_type = "application/octet-stream"

            with open(file_path, "rb") as file:
                self.send_response(200)
                self.send_header("Content-type", content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, f"Static File Not Found: {file_path}")


def main():
    # Socket server
    threading.Thread(target=socket_server, daemon=True).start()

    # HTTP server
    httpd = HTTPServer(("0.0.0.0", PORT_H), SimpleHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
