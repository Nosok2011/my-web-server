from subprocess import Popen
from config import htdocs, php_port
from time import sleep
class PHPServer:
    def start_server(self):
        print("starting PHP server")
        self.server = Popen(["php", "-S", f"localhost:{php_port}", "-t", htdocs])
        sleep(0.05) # дождаться загрузки сервера
    def stop_server(self):
        print("stopping PHP server")
        self.server.terminate()