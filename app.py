from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import json
import os
import tempfile
import shutil
from utils.dashboard import initialize, configured_mode, set_mode, save_detection

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["ALERTA_KEY"] = os.environ.get("ALERTA_KEY")
initialize(app)

# Estado en la carpeta de datos o en el volumen conectado a Railway.
TMP_DIR = str(app.config["MONITOR_DATA_DIR"])
USUARIOS_FILE = os.path.join(TMP_DIR, "usuarios.json")
ESTADOS_FILE = os.path.join(TMP_DIR, "estados.json")
for name in ("usuarios.json", "estados.json"):
    old_path = os.path.join(tempfile.gettempdir(), name)
    new_path = os.path.join(TMP_DIR, name)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        shutil.copyfile(old_path, new_path)

# Variables de entorno esperadas
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")  # e.g. "whatsapp:+1415xxxxxxx"
ALERTA_KEY = os.environ.get("ALERTA_KEY")  # secreto para proteger /alerta

def cargar_json(ruta):
    try:
        if not os.path.exists(ruta):
            # asegúrate que exista el archivo con un diccionario vacío
            with open(ruta, "w") as f:
                json.dump({}, f)
        with open(ruta, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        app.logger.warning(f"Error cargando JSON {ruta}: {e}")
        return {}

def guardar_json(ruta, data):
    try:
        with open(ruta, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        app.logger.error(f"Error guardando JSON {ruta}: {e}")

def enviar_whatsapp(numero_destino, texto):
    """
    Envía WhatsApp usando Twilio REST API.
    numero_destino debe tener el formato: 'whatsapp:+51...' o 'whatsapp:+1...'
    """
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_WHATSAPP_FROM):
        app.logger.error("Credenciales Twilio no están configuradas en variables de entorno.")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            body=texto,
            to=numero_destino
        )
        app.logger.info(f"Mensaje Twilio SID: {message.sid} enviado a {numero_destino}")
        return True
    except Exception as e:
        app.logger.error(f"Error enviando WhatsApp: {e}")
        return False

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    from_number = request.values.get("From", "")
    incoming_msg = request.values.get("Body", "").strip().lower()

    usuarios = cargar_json(USUARIOS_FILE)
    estados = cargar_json(ESTADOS_FILE)

    resp = MessagingResponse()
    msg = resp.message()

    # Registrar usuarios
    if incoming_msg.startswith("join"):
        usuarios[from_number] = True
        guardar_json(USUARIOS_FILE, usuarios)
        msg.body("🟢 *Registro exitoso*\nTu número ha sido registrado y ahora recibirás alertas.")
        return str(resp)

    # Menú
    if incoming_msg in ["menu", "hola", "inicio"]:
        texto = (
            "🟢 *Monitoreo de especies*\n\n"
            "¿Qué deseas monitorear hoy?\n"
            "1️⃣ Tortugas 🐢\n"
            "2️⃣ Gaviotines 🐦\n\n"
            "Responde con *1* o *2*."
        )
        msg.body(texto)
        return str(resp)

    # Elección del usuario
    if incoming_msg in ["1", "tortugas"]:
        estados[from_number] = "tortugas"
        guardar_json(ESTADOS_FILE, estados)
        set_mode("tortugas")
        msg.body("Has elegido 🐢 *Tortugas*. El sistema iniciará la detección.")
        return str(resp)

    if incoming_msg in ["2", "gaviotines"]:
        estados[from_number] = "gaviotines"
        guardar_json(ESTADOS_FILE, estados)
        set_mode("gaviotines")
        msg.body("Has elegido 🐦 *Gaviotines*. El sistema iniciará la detección.")
        return str(resp)

    msg.body("No entendí tu mensaje. Escribe *menu* para ver opciones.")
    return str(resp)

@app.route("/config", methods=["GET"])
def obtener_configuracion():
    """
    La Raspberry Pi consulta este endpoint para saber qué especie monitorear.
    Devuelve {"mode": "tortugas"} por ejemplo.
    """
    estados = cargar_json(ESTADOS_FILE)
    mode = configured_mode() or (list(estados.values())[-1] if estados else "tortugas")
    return jsonify({"mode": mode})

@app.route("/alerta", methods=["POST"])
def recibir_alerta():
    """
    Endpoint que la Raspberry Pi usa para notificar detecciones.
    """
    if ALERTA_KEY:
        header_key = request.headers.get("X-ALERTA-KEY", "")
        if header_key != ALERTA_KEY:
            app.logger.warning("Intento de acceso a /alerta con llave inválida")
            return jsonify({"error": "Unauthorized"}), 401
    
    try:
        data = request.get_json(force=True)
        especie = data.get("especie", "tortugas")
        cantidad = data.get("cantidad", 1)
        imagen_url = data.get("imagen", None)
    except Exception as e:
        app.logger.error(f"Error parsing JSON en /alerta: {e}")
        return jsonify({"error": "bad request"}), 400

    try:
        save_detection(data)
    except ValueError as error:
        app.logger.warning("Alerta sin registro en el dashboard: %s", error)
    
    usuarios = cargar_json(USUARIOS_FILE)
    if not usuarios:
        app.logger.info("No hay usuarios registrados.")
        return jsonify({"status": "no_users"}), 200
    
    # Preparar mensaje
    texto = f"🚨 *DETECCIÓN AUTOMÁTICA*\n\nEspecie: *{especie}*\nCantidad: *{cantidad}*"
    if imagen_url:
        texto += "\n\n📸 Imagen adjunta."
    
    enviado_a = []
    fallos = []
    
    # Enviar con imagen si existe
    for numero in usuarios.keys():
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            msg_params = {
                "from_": TWILIO_WHATSAPP_FROM,
                "body": texto,
                "to": numero
            }
            
            if imagen_url:
                msg_params["media_url"] = [imagen_url]
            
            message = client.messages.create(**msg_params)
            app.logger.info(f"Mensaje enviado a {numero}: {message.sid}")
            enviado_a.append(numero)
        except Exception as e:
            app.logger.error(f"Error enviando a {numero}: {e}")
            fallos.append(numero)
    
    return jsonify({"status": "ok", "enviados": enviado_a, "fallos": fallos}), 200

if __name__ == "__main__":
    # puerto dinámico para Railway y otros hosts
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





