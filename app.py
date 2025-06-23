import os

# Solo en desarrollo local usa python-dotenv
if os.getenv("VERCEL") is None:   # Vercel define esta var en su entorno
    from dotenv import load_dotenv
    load_dotenv()                 # cargará tu .env local si existe


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
