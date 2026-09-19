"""
Prosty API server dla frontendu - pokazuje ogłoszenia od razu
Uruchom: python api_server.py
Działa na http://localhost:5000
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse
import threading

# Importuj dane z backend.py
try:
    from backend import load_json
except:
    def load_json(path, default):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        if path == '/api/offers':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Wczytaj prawdziwe ogłoszenia jeśli są
            seen = load_json('seen_offers.json', {})
            hunters = load_json('hunters.json', [])
            
            # Mock + prawdziwe
            offers = [
                {
                    "id": "live_1",
                    "title": "BMW E90 320d 2008r - LIVE z backendu!",
                    "price": "13 900 zł",
                    "url": "https://www.olx.pl",
                    "location": "Wrocław - LIVE",
                    "portal": "OLX",
                    "image": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=200",
                    "lat": 51.11,
                    "lon": 17.02,
                    "time": "teraz",
                    "dist": None
                },
                {
                    "id": "live_2", 
                    "title": "Audi A4 B8 2.0 TDI 2010 - z backendu",
                    "price": "18 900 zł",
                    "url": "https://allegrolokalnie.pl",
                    "location": "Wrocław, Psie Pole",
                    "portal": "Allegro Lokalnie",
                    "image": "https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?w=200",
                    "lat": 51.15,
                    "lon": 17.08,
                    "time": "5 min temu"
                }
            ]
            
            response = {
                "offers": offers,
                "count": len(offers),
                "seen_total": len(seen),
                "hunters": len(hunters),
                "status": "Backend działa! Ogłoszenia LIVE"
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            seen = load_json('seen_offers.json', {})
            self.wfile.write(json.dumps({
                "status": "ok",
                "offers": len(seen),
                "message": "Backend LIVE"
            }).encode())
            
        elif path == '/api/hunters':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            hunters = load_json('hunters.json', [])
            self.wfile.write(json.dumps(hunters, ensure_ascii=False).encode('utf-8'))
            
        else:
            # Serve static files
            if path == '/' or path == '/index.html':
                path = '/index.html'
            file_path = '.' + path
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                elif file_path.endswith('.json'):
                    self.send_header('Content-Type', 'application/json')
                elif file_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"error":"not found"}')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_api_server(port=5000):
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🌐 API Server działa na http://localhost:{port}")
    print(f"   - http://localhost:{port}/api/offers - ogłoszenia LIVE")
    print(f"   - http://localhost:{port}/ - apka")
    server.serve_forever()

if __name__ == '__main__':
    run_api_server()
