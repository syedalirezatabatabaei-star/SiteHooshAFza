"""Static file server for the هوش افزا frontend (local development preview)."""
import http.server
import os
import sys
import socketserver
from pathlib import Path
from urllib.parse import urlsplit, unquote

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
MEDIA_ROOT = Path(__file__).resolve().parent / 'backend' / 'media'


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        # "/" → index.html
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        # /login, /register etc → /pages/login.html (clean URLs)
        if not os.path.splitext(self.path)[1] and not self.path.startswith("/css") \
                and not self.path.startswith("/js") and not self.path.startswith("/assets"):
            clean = self.path.lstrip("/")
            if clean and os.path.exists(os.path.join(ROOT, "pages", clean + ".html")):
                self.path = "/pages/" + clean + ".html"
        super().do_GET()

    def translate_path(self, path):
        url_path = unquote(urlsplit(path).path)
        if url_path.startswith('/media/'):
            candidate = (MEDIA_ROOT / url_path[len('/media/'):]).resolve()
            if not candidate.is_relative_to(MEDIA_ROOT.resolve()):
                return str(MEDIA_ROOT / '__invalid_path__')
            return str(candidate)
        return super().translate_path(path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, format, *args):
        pass  # keep log quiet


class ReusableTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Frontend serving {ROOT} at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
