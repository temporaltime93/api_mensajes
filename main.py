from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)  # * Habilita CORS para todos los dominios

@app.route('/')
def home():
    return "✅ API M3U8 Activa"

@app.route('/get-m3u8', methods=['GET'])
def get_m3u8():
    link = request.args.get('link')

    if not link:
        return jsonify({'error': 'Falta el parámetro "link"'}), 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }

        response = requests.get(link, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # ? Buscar cualquier m3u8 en el contenido de la página
        matches = re.findall(r'(https?:\/\/[^\s\'"]+\.m3u8)', soup.prettify())

        if not matches:
            return jsonify({'error': 'No se encontró ningún enlace .m3u8'}), 404

        return jsonify({'m3u8': matches[0]})

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error al hacer la solicitud: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
