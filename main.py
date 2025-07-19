from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/get-m3u8")
def get_m3u8():
    page_url = request.args.get("link")
    if not page_url:
        return jsonify({"error": "Falta el parámetro 'link'"}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(page_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup.find_all("source"):
            src = tag.get("src")
            if src and ".m3u8" in src:
                return jsonify({"found": True, "m3u8": src})

        return jsonify({"found": False, "message": "No se encontró enlace .m3u8"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

app.run(host="0.0.0.0", port=3000)
