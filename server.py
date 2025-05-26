#!/usr/bin/python3.13
import socket
import http_headers
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
class Server:
    def __init__(self, addr="0.0.0.0", port=3000, main_dir="./web", index_file="index.html"):
        self.srv_addr = addr
        self.srv_port = port
        self.main_dir = main_dir
        self.index_file = index_file
    def start_server(self):
        print("starting server")
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.srv_addr, self.srv_port))
        self.server_sock.listen()
        all_addrs = True if self.srv_addr == "0.0.0.0" else False
        print(f"server started on {"all addresses" if all_addrs else self.srv_addr}, port {self.srv_port}")
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
                path = self.main_dir + data.split()[1] 
                print(self.index_file, path)
                content = self.get_page(path)
                client_sock.sendall(content.encode())
                client_sock.shutdown(socket.SHUT_RDWR)
                client_sock.close()
                del self.clients[self.clients.index(client_sock)]
        except KeyboardInterrupt:
            self.stop_server()
    def get_page(self, path):
        try:
            content = open(self.main_dir + path, encoding="UTF-8").read()
            return http_headers.http_ok + content
        except FileNotFoundError:
            print(path)
            print(os.getcwd())
            if not path.endswith("favicon.ico"):
                return http_headers.http_not_found + "<h1>error: file not found</h1>"
        except PermissionError:
            return http_headers.http_forbidden + "<h1>error: permisson denied</h1>"
        except IsADirectoryError: # TODO: добавить проверку на наличие файла index.html и отображение папок и файлов при его отсутствии
            #if os.path.isfile(path + "/" if not path.endswith("/") else "" + self.index_file):
            print(path, path + ("/" if not path.endswith("/") else "") + self.index_file, os.path.isfile(path + "/" if not path.endswith("/") else "" + self.index_file))
            return http_headers.http_error + "<h1>error: tried to open a directory as a file</h1>"
        except Exception as e:
            return http_headers.http_error + f"<h1>error: unknown error</h1><p>{e}</p>"
    def get_html_files_list(self, path):
        ...
    def stop_server(self):
        print("stopping server")
        if self.clients:
            print("disconnecting clients")
            for client in self.clients:
                client.sendall((http_headers.http_server_is_down + "<h1>sorry, the server is shutting down</h1>").encode())
                client.shutdown(socket.SHUT_RDWR)
                client.close()
        self.server_sock.shutdown(socket.SHUT_RDWR)
        self.server_sock.close()
        sys.exit()
if __name__ == "__main__":
    server = Server()
    server.start_server()