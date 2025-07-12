from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # * Permite conexiones desde apps móviles

# * Almacén simple en memoria
messages = []

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def post_message():
    data = request.json
    text = data.get("text", "")
    if text:
        messages.append(text)
        return jsonify({"success": True}), 201
    return jsonify({"success": False, "error": "No text provided"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
