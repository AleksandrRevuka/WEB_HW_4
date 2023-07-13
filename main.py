from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

import urllib.parse
import mimetypes
import pathlib
import socket
import json
import threading

UDP_IP = "127.0.0.1"
UDP_PORT = 5000
SERVER_PORT = 3000

class HTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/goit":
            self.send_response(302)
            self.send_header("Location", "https://www.goit.global/")
            self.end_headers()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static_file()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self) -> None:
        data = self.rfile.read(int(self.headers["Content-Length"]))
        send_data_via_socket(data)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200) -> None:
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as file_descriptor:
            self.wfile.write(file_descriptor.read())

    def send_static_file(self) -> None:
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http_server(server_class=HTTPServer, handler_class=HTTPHandler) -> None:
    server_address = ("", SERVER_PORT)
    http_server = server_class(server_address, handler_class)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()


def save_to_json(data: dict) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open("storage/data.json", "r+") as file:
        existing_data = json.load(file)
        existing_data[now] = data

        file.seek(0)
        json.dump(existing_data, file, indent=4)


def normalize_data(data: bytes) -> dict[str, str]:
    decoded_data = urllib.parse.unquote_plus(data.decode())
    parsed_data = {
        key: value for key, value in [el.split("=") for el in decoded_data.split("&")]
    }
    return parsed_data


def run_socket_server(ip=UDP_IP, port=UDP_PORT) -> None:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ip, port
    udp_socket.bind(server_address)
    try:
        while True:
            data, address = udp_socket.recvfrom(1024)
            data_dict: dict = normalize_data(data)
            save_to_json(data_dict)

    except KeyboardInterrupt:
        print(f"Destroy server: {address}")
    finally:
        udp_socket.close()


def send_data_via_socket(data, ip=UDP_IP, port=UDP_PORT) -> None:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ip, port
    udp_socket.sendto(data, server_address)


if __name__ == "__main__":
    http_thread = threading.Thread(target=run_http_server)
    socket_thread = threading.Thread(target=run_socket_server)
    http_thread.start()
    socket_thread.start()
    http_thread.join()
    socket_thread.join()
