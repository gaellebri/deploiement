# app.py
from flask import Flask, render_template_string, jsonify, request, redirect, url_for
from datetime import datetime
import socket
import os
import json
from pathlib import Path

app = Flask(__name__)

# Chemin vers le répertoire de données persistantes
DATA_DIR = Path('/app/data')
DATA_DIR.mkdir(exist_ok=True)

# Fichiers de données
VISITORS_FILE = DATA_DIR / 'visitors.json'
MESSAGES_FILE = DATA_DIR / 'messages.json'

# Initialiser les fichiers s'ils n'existent pas
if not VISITORS_FILE.exists():
    with open(VISITORS_FILE, 'w') as f:
        json.dump({'count': 0, 'visits': []}, f)

if not MESSAGES_FILE.exists():
    with open(MESSAGES_FILE, 'w') as f:
        json.dump([], f)

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
        .message-form {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .message-form input, .message-form textarea {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 3px;
            box-sizing: border-box;
        }
        .message-form button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }
        .message-form button:hover {
            background-color: #0056b3;
        }
        .messages {
            max-height: 300px;
            overflow-y: auto;
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
        }
        .message {
            background-color: white;
            padding: 10px;
            margin: 5px 0;
            border-radius: 3px;
            border-left: 3px solid #007bff;
        }
        .counter {
            font-size: 24px;
            color: #007bff;
            text-align: center;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Application Test Conteneur avec Volume Persistant</h1>
        <p class="status">✅ L'application fonctionne correctement !</p>
        
        <div class="counter">
            👥 Nombre total de visites : {{ visitor_count }}
        </div>
        
        <div class="info-box">
            <h2>Informations système</h2>
            <p><strong>Heure actuelle :</strong> {{ current_time }}</p>
            <p><strong>Hostname :</strong> {{ hostname }}</p>
            <p><strong>Adresse IP du conteneur :</strong> {{ container_ip }}</p>
        </div>
        
        <div class="message-form">
            <h2>Laisser un message (persistant)</h2>
            <form method="POST" action="/message">
                <input type="text" name="author" placeholder="Votre nom" required>
                <textarea name="content" placeholder="Votre message" rows="3" required></textarea>
                <button type="submit">Envoyer</button>
            </form>
        </div>
        
        <div class="info-box">
            <h2>Messages récents (stockés dans /app/data)</h2>
            <div class="messages">
                {% if messages %}
                    {% for msg in messages[-5:] | reverse %}
                    <div class="message">
                        <strong>{{ msg.author }}</strong> - {{ msg.timestamp }}<br>
                        {{ msg.content }}
                    </div>
                    {% endfor %}
                {% else %}
                    <p>Aucun message pour le moment.</p>
                {% endif %}
            </div>
        </div>
        
        <div class="info-box">
            <h2>Endpoints disponibles</h2>
            <div class="endpoint">GET / - Page d'accueil (cette page)</div>
            <div class="endpoint">POST /message - Ajouter un message</div>
            <div class="endpoint">GET /api/status - Status de l'application (JSON)</div>
            <div class="endpoint">GET /api/info - Informations système (JSON)</div>
            <div class="endpoint">GET /api/messages - Liste des messages (JSON)</div>
            <div class="endpoint">GET /api/stats - Statistiques de visite (JSON)</div>
            <div class="endpoint">GET /health - Health check</div>
        </div>
    </div>
</body>
</html>
"""

def load_visitors():
    """Charger les statistiques de visite"""
    with open(VISITORS_FILE, 'r') as f:
        return json.load(f)

def save_visitors(data):
    """Sauvegarder les statistiques de visite"""
    with open(VISITORS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_messages():
    """Charger les messages"""
    with open(MESSAGES_FILE, 'r') as f:
        return json.load(f)

def save_messages(messages):
    """Sauvegarder les messages"""
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

def record_visit():
    """Enregistrer une visite"""
    visitors = load_visitors()
    visitors['count'] += 1
    visitors['visits'].append({
        'timestamp': datetime.now().isoformat(),
        'ip': request.remote_addr
    })
    # Garder seulement les 100 dernières visites
    visitors['visits'] = visitors['visits'][-100:]
    save_visitors(visitors)
    return visitors['count']

@app.route('/')
def home():
    """Page d'accueil avec informations système"""
    visitor_count = record_visit()
    messages = load_messages()
    
    return render_template_string(HTML_TEMPLATE,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hostname=socket.gethostname(),
        container_ip=socket.gethostbyname(socket.gethostname()),
        visitor_count=visitor_count,
        messages=messages
    )

@app.route('/message', methods=['POST'])
def add_message():
    """Ajouter un message"""
    author = request.form.get('author', 'Anonyme')
    content = request.form.get('content', '')
    
    if content:
        messages = load_messages()
        messages.append({
            'author': author,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        # Garder seulement les 50 derniers messages
        messages = messages[-50:]
        save_messages(messages)
    
    return redirect(url_for('home'))

@app.route('/api/status')
def api_status():
    """Endpoint API pour le status de l'application"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'data_directory': str(DATA_DIR),
        'data_files': [str(f.name) for f in DATA_DIR.iterdir()]
    })

@app.route('/api/info')
def api_info():
    """Endpoint API pour les informations système"""
    return jsonify({
        'hostname': socket.gethostname(),
        'ip_address': socket.gethostbyname(socket.gethostname()),
        'python_version': os.sys.version,
        'data_directory': str(DATA_DIR),
        'environment': dict(os.environ)
    })

@app.route('/api/messages')
def api_messages():
    """Endpoint API pour récupérer les messages"""
    messages = load_messages()
    return jsonify(messages)

@app.route('/api/stats')
def api_stats():
    """Endpoint API pour les statistiques"""
    visitors = load_visitors()
    return jsonify(visitors)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Important: écouter sur toutes les interfaces (0.0.0.0) pour permettre l'accès externe
    app.run(host='0.0.0.0', port=5000, debug=True)