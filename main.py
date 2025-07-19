from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)  # * Permite llamadas desde otros dominios (CORS)

# * Función para extraer .m3u8
def extraer_m3u8(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text

        # ? Busca cualquier link que termine en .m3u8
        m3u8_links = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', html)
        return m3u8_links[0] if m3u8_links else None
    except Exception as e:
        return None

@app.route('/get-m3u8', methods=['GET'])
def get_m3u8():
    link = request.args.get('link')
    if not link:
        return jsonify({"error": "No se proporcionó el parámetro 'link'"}), 400

    result = extraer_m3u8(link)
    if result:
        return jsonify({"m3u8": result})
    else:
        return jsonify({"error": "No se encontró ningún link m3u8"}), 404

if __name__ == '__main__':
    app.run()
