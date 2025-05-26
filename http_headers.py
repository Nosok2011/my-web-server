class Headers:
    http_codes = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }
    def __init__(self, code):
        self.code = code
    def generate_http_header(self):
        return f"HTTP/1.1 {self.code} {self.http_codes[self.code]}\r\nContent-Type: text/html; charset=utf-8\r\n\r\n"
http_ok = Headers(200).generate_http_header()
http_forbidden = Headers(403).generate_http_header()
http_not_found = Headers(404).generate_http_header()
http_error = Headers(500).generate_http_header()
http_server_is_down = Headers(503).generate_http_header()