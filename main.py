from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)  # * Habilita CORS para todos los dominios

@app.route("/")
def index():
    return "API M3U8 activa"

@app.route("/get-m3u8")
def get_m3u8():
    url = request.args.get("link")
    if not url:
        return jsonify({"error": "Falta el parámetro link"}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        html = response.text

        match = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', html)
        if match:
            return jsonify({
                "found": True,
                "m3u8": match.group(1)
            })
        else:
            return jsonify({
                "found": False,
                "message": "No se encontró un enlace M3U8."
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
