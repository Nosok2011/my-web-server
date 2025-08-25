#!/usr/bin/env python3
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
import config
from os import chdir, listdir
from os.path import dirname, abspath, isfile
from sys import exit
from traceback import print_exc, format_exc
from php_server import PHPServer
from requests import get
chdir(dirname(abspath(__file__)))
class Server:
    def start_server(self):
        print("starting server")
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock.bind((config.ip, config.port))
        self.server_sock.listen()
        all_addrs = True if config.ip == "0.0.0.0" else False
        print(f"server started on {"all addresses" if all_addrs else config.ip}, port {config.port}")
        print("press ctrl+c to stop server")
        self.handle_requests()
    def handle_requests(self):
        self.clients = []
        try:
            while True:
                client_sock, client_addr = self.server_sock.accept()
                self.clients.append(client_sock)
                client_ip, client_port = client_addr
                print(f"new request from {client_ip}:{client_port}")
                data = client_sock.recv(1024).decode()
                if not data:
                    print("no data, disconnect client and wait for next request")
                    client_sock.close()
                    del self.clients[self.clients.index(client_sock)]
                    continue
                print(data)
                path = config.htdocs + data.split()[1]
                content = self.get_page(path)
                client_sock.sendall(content.encode())
                client_sock.shutdown(SHUT_RDWR)
                client_sock.close()
                del self.clients[self.clients.index(client_sock)]
        except KeyboardInterrupt:
            self.stop_server()
    def get_page(self, path):
        path2 = path.replace(config.htdocs, "")
        try:
            with open(path, encoding="UTF-8") as page:
                if isfile(path) and path.endswith(".php"):
                    content = self.handle_php(path)
                else:
                    content = page.read()
        except FileNotFoundError as e:
            print_exc()
            with open(f"{config.service_dir}/notfound.html", encoding="UTF-8") as notfound:
                notfound = notfound.read()
            return config.http_not_found + notfound.replace("{path}", path2)
        except PermissionError as e:
            print_exc()
            with open(f"{config.service_dir}/permdenied.html", encoding="UTF-8") as permdenied:
                permdenied = permdenied.read()
            return config.http_forbidden + permdenied.replace("{path}", path2)
        except IsADirectoryError as e:
            if isfile(path + "/" + config.index_file):
                with open(path + "/" + config.index_file) as index:
                    content = index.read()
            else:
                content = self.get_html_files_list(path)
        except Exception as e:
            print_exc()
            with open(f"{config.service_dir}/internal.html", encoding="UTF-8") as internal:
                internal = internal.read()
            return config.http_internal + internal.replace("{err}", format_exc().replace("<", "&lt;").replace(">", "&gt;"))
        return config.http_ok + content
    def handle_php(self, path):
        php = PHPServer()
        php.start_server()
        php_handled = get(f"http://localhost:{config.php_port}/{path.replace(config.htdocs, "").lstrip("/")}").text
        php.stop_server()
        return php_handled
    def get_html_files_list(self, path):
        with open(f"{config.service_dir}/list_of_files.html", encoding="UTF-8") as tpl_:
            tpl = tpl_.read() # tpl - template
        path2 = path.replace(config.htdocs, "")
        tpl2 = tpl.replace("{dir}", path2)
        lst = [f"<li><a href=\"{path2}{"/" if not path2.endswith("/") else ""}{file}\">{file}</a></li>" for file in listdir(path)]
        page = tpl2.replace("{list}", "".join(lst))
        return page
    def stop_server(self):
        print("stopping server")
        if self.clients:
            with open(f"{config.service_dir}/shuttingdown.html", encoding="UTF-8") as shuttingdown:
                shuttingdown = shuttingdown.read()
            print("disconnecting clients")
            for client in self.clients:
                client.sendall((config.http_unavailable + shuttingdown).encode())
                client.shutdown(SHUT_RDWR)
                client.close()
        self.server_sock.shutdown(SHUT_RDWR)
        self.server_sock.close()
        exit()
if __name__ == "__main__":
    server = Server()
    server.start_server()