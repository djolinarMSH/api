# /api/get_alerts.py
import os
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Отримуємо секретний API ключ з середовища Vercel (це безпечно)
        API_TOKEN = os.environ.get('ALERTS_API_KEY')
        ALARM_API_URL = "https://api.alerts.in.ua/v1/alerts/active.json"

        if not API_TOKEN:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'API token not configured on the server'}).encode('utf-8'))
            return

        headers = {"Authorization": f"Bearer {API_TOKEN}"}
        
        try:
            response = requests.get(ALARM_API_URL, headers=headers, timeout=10)
            response.raise_for_status() # Перевірка на помилки HTTP (4xx, 5xx)
            
            # Надсилаємо відповідь клієнту
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            # Додаємо заголовок для кешування на стороні клієнта та проксі (на 20 секунд)
            self.send_header('Cache-Control', 's-maxage=20, stale-while-revalidate')
            self.end_headers()
            self.wfile.write(response.content)

        except requests.RequestException as e:
            self.send_response(502) # Bad Gateway
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Failed to fetch data from alerts API', 'details': str(e)}).encode('utf-8'))