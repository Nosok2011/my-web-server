from http_headers import *
from os import getcwd
index_file = "index.html"
htdocs = f"{getcwd()}/web" # на конце слэш не ставим
ip = "0.0.0.0"
port = 3000
php_port = 3001
service_dir = f"{getcwd()}/service" # тут тоже