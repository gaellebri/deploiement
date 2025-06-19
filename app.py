# app.py
from flask import Flask, render_template_string, jsonify
from datetime import datetime
import socket
import os

app = Flask(__name__)

# Template HTML pour la page d'accueil
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application Test Conteneur</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .info-box {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .endpoint {
            background-color: #f0f0f0;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-family: monospace;
        }
        .status {
            color: #28a745;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Application Test Conteneur</h1>
        <p class="status">✅ L'application fonctionne correctement !</p>
        
        <div class="info-box">
            <h2>Informations système</h2>
            <p><strong>Heure actuelle :</strong> {{ current_time }}</p>
            <p><strong>Hostname :</strong> {{ hostname }}</p>
            <p><strong>Adresse IP du conteneur :</strong> {{ container_ip }}</p>
        </div>
        
        <div class="info-box">
            <h2>Endpoints disponibles</h2>
            <div class="endpoint">GET / - Page d'accueil (cette page)</div>
            <div class="endpoint">GET /api/status - Status de l'application (JSON)</div>
            <div class="endpoint">GET /api/info - Informations système (JSON)</div>
            <div class="endpoint">GET /health - Health check</div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Page d'accueil avec informations système"""
    return render_template_string(HTML_TEMPLATE,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hostname=socket.gethostname(),
        container_ip=socket.gethostbyname(socket.gethostname())
    )

@app.route('/api/status')
def api_status():
    """Endpoint API pour le status de l'application"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/info')
def api_info():
    """Endpoint API pour les informations système"""
    return jsonify({
        'hostname': socket.gethostname(),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'python_version': os.sys.version,
        'environment': dict(os.environ)
    })
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Important: écouter sur toutes les interfaces (0.0.0.0) pour permettre l'accès externe
    app.run(host='0.0.0.0', port=8000, debug=True)