from flask import Flask, jsonify, render_template
import os
import socket
from datetime import datetime

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "Development")
DEPLOYMENT_COLOR = os.getenv("DEPLOYMENT_COLOR", "BLUE")


@app.route("/")
def home():
    return render_template(
        "index.html",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        hostname=socket.gethostname(),
        deployment_color=DEPLOYMENT_COLOR
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "CloudOps Dashboard",
        "version": APP_VERSION,
        "deployment_color": DEPLOYMENT_COLOR,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route("/api/info")
def info():
    return jsonify({
        "application": "CloudOps Dashboard",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "hostname": socket.gethostname(),
        "platform": "Kubernetes",
        "deployment_color": DEPLOYMENT_COLOR
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
