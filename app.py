import os
from pathlib import Path

# ─── Cargar credenciales desde archivo externo ───
# Ajusta este path según dónde guardaste secrets.txt
secrets_path = Path.home() / "secrets" / "secrets.txt"

if secrets_path.exists():
    for line in secrets_path.read_text().splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, val = line.split("=", 1)
        # No sobreescribimos vars ya definidas
        os.environ.setdefault(key.strip(), val.strip())
else:
    raise FileNotFoundError(f"No se encontró el archivo de secretos en: {secrets_path}")


from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from utils.config import Config
from routes.pstn_routes import pstn_bp
from routes.webhook_routes import webhook_bp

app = Flask(__name__)
CORS(app, resources={
    r"/pstn": {
        "origins": Config.ALLOWED_ORIGINS.split(','),
        "allow_headers": "*",
        "expose_headers": "*"
    },
    r"/*": {
        "origins": "*",
        "allow_headers": "*",
        "expose_headers": "*"
    }
})

# Register blueprints
app.register_blueprint(pstn_bp)
app.register_blueprint(webhook_bp)

@app.route('/')
def index():
    """Render the main index page"""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
