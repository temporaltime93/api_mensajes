import os
import json
import threading
import requests
import discord
from discord.ext import commands
from flask import Flask, request
from flask_cors import CORS

# ===================== 🔧 CONFIGURACIÓN ======================

WEBHOOK_URL = os.getenv("LINK")
CLAVE_SECRETA = "baSLsVSrMMfxlfAdleg6Lqey9N5G"

URL_JSON = "https://raw.githubusercontent.com/temporaltime93/bot/refs/heads/main/valor.json"



# ===================== 🌐 API FLASK ======================

app = Flask(__name__)
CORS(app)

def mensaje(placeNb, Name_user, Informacion):
    try:
        response = requests.get(URL_JSON)
        response.raise_for_status()
        valores = response.json()
    except Exception as e:
        return f"❌ Error al obtener JSON remoto: {e}", 500

    if placeNb not in valores:
        return f"❌ La clave '{placeNb}' no está registrada en valor.json", 400

    ID = valores[placeNb]["ID"]
    ST = valores[placeNb]["SCRIPT"]

    EMBEB = {
        "content": f"||# Holiiiii...! <@{Name_user}>||",
        "allowed_mentions": {"users": [Name_user]},
        "embeds": [
            {
                "title": "Holiiiii...!",
                "description": f"""```ansi
[2;35m[1;35mVengo a avisarte por parte del script("{ST}") para decirte que:[0m

[2;34m[1;34m----------->

{Informacion}
----------->[0m[2;34m[0m
                                                 
[1;2m[1;35m[1;35m¡Bueno, eso era todo, bye! No olvides de recomendarnos con tus amigos shiii~[0m[1;35m[0m[0m                                                            
```""",
                "color": 13948116,
                "image": {
                    "url": "https://firebasestorage.googleapis.com/v0/b/fotos-b8a54.appspot.com/o/Frame%2014%20(1)%201.png?alt=media&token=b0636b4e-ffab-4c77-9b76-2b082981df84"
                }
            }
        ],
    }

    try:
        resp = requests.post(WEBHOOK_URL, json=EMBEB, params={"thread_id": ID})
        if resp.status_code in (200, 204):
            return "✅ Mensaje enviado al hilo de Discord", 200
        else:
            return f"❌ Error al enviar mensaje: {resp.status_code}\n{resp.text}", 500
    except Exception as e:
        return f"❌ Error en el servidor: {str(e)}", 500

@app.route("/enviar", methods=["GET"])
def enviar():
    clave = request.args.get("Nkart", "")
    _placeNb_ = request.args.get("IPFUEOPjd", "")
    _Name_user_ = request.args.get("davvgfrF", "")
    _Informacion_ = request.args.get("OIHDoihio", "")
    ua = request.headers.get("User-Agent", "")
    if not ua.startswith("Roblox"):
        return "❌ Origen no permitido", 403
    if clave != CLAVE_SECRETA:
        return "❌ Clave incorrecta. No autorizado.", 403

    return mensaje(_placeNb_, _Name_user_, _Informacion_)

# ===================== 🚀 INICIAR BOT Y API ======================

# def run_flask():
#     app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)