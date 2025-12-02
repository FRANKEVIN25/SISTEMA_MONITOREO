import os
import time
import json
import cv2
import numpy as np
import requests
from ultralytics import YOLO
from utils.send_alert import enviar_alerta
from dotenv import load_dotenv  # <-- DEBE ESTAR AQUÍ

# CONFIGURACIÓN
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
MODELS_DIR = os.path.join(PROJECT_DIR, "modelos")

# Cargar variables de entorno
load_dotenv(os.path.join(PROJECT_DIR, '.env'))  # <-- AHORA SÍ SE PUEDE USAR

# URL de Railway
RAILWAY_URL = os.environ.get("RAILWAY_URL", "http://localhost:5000")
def get_mode():
    """Consulta Railway para saber qué especie monitorear"""
    try:
        response = requests.get(f"{RAILWAY_URL}/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            mode = data.get("mode", "tortugas")
            print(f"✅ Modo obtenido de Railway: {mode}")
            return mode
    except Exception as e:
        print(f"⚠️ Error consultando Railway: {e}")
    
    # Fallback local
    try:
        config_path = os.path.join(PROJECT_DIR, "data", "config.json")
        with open(config_path, "r") as f:
            data = json.load(f)
        return data.get("mode", "tortugas")
    except:
        return "tortugas"

def cargar_modelo(mode):
    """Carga el modelo YOLO"""
    modelo_path = os.path.join(MODELS_DIR, f"{mode}.pt")
    
    if not os.path.exists(modelo_path):
        print(f"❌ ERROR: No se encontró el modelo: {modelo_path}")
        exit()
    
    print(f"📦 Cargando modelo: {mode}")
    return YOLO(modelo_path)

def iniciar_camara():
    """Activa la cámara Raspberry Pi Camera Module o USB"""
    # Intentar Camera Module (CSI)
    try:
        from picamera2 import Picamera2
        
        picam2 = Picamera2()
        # Configuración optimizada para rendimiento
        config = picam2.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"},
            buffer_count=2  # Reduce buffering
        )
        picam2.configure(config)
        picam2.start()
        time.sleep(1)  # Reducido de 2 a 1 segundo
        
        print("🎥 Camera Module CSI iniciada. Presiona 'q' para salir.")
        return picam2, "picamera"
    except Exception as e:
        print(f"⚠️ Camera Module no disponible: {e}")
    
    # Fallback a cámara USB
    print("🔄 Intentando cámara USB...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        # Optimizar configuración USB
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag
        
        print("🎥 Cámara USB iniciada. Presiona 'q' para salir.")
        return cap, "usb"
    
    print("❌ No se pudo acceder a ninguna cámara.")
    exit()

def capturar_frame(cap, tipo_camara):
    """Captura un frame según el tipo de cámara"""
    if tipo_camara == "picamera":
        frame = cap.capture_array()
        # Convertir de RGB a BGR para OpenCV
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return True, frame
    else:  # USB
        return cap.read()

def liberar_camara(cap, tipo_camara):
    """Libera la cámara según el tipo"""
    if tipo_camara == "picamera":
        cap.stop()
    else:
        cap.release()
    cv2.destroyAllWindows()

def main():
    especie_actual = None
    model = None
    cap, tipo_camara = iniciar_camara()
    
    ultimo_envio = 0
    tiempo_espera = 20
    
    # Optimización: consultar Railway cada N frames en lugar de cada loop
    frame_count = 0
    check_railway_every = 30  # Consulta Railway cada 30 frames (~1 segundo)
    
    print(f"📹 Usando cámara tipo: {tipo_camara}")
    
    try:
        while True:
            # Solo consultar Railway cada 30 frames
            if frame_count % check_railway_every == 0:
                especie = get_mode()
                
                if especie != especie_actual:
                    print(f"\n🔄 Nuevo modo: {especie}")
                    especie_actual = especie
                    model = cargar_modelo(especie_actual)
            
            frame_count += 1
            
            ret, frame = capturar_frame(cap, tipo_camara)
            if not ret or frame is None:
                print("⚠️ Error al capturar frame.")
                break
            
            # Optimización: reducir tamaño si es muy grande
            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                frame = cv2.resize(frame, (640, int(height * scale)))
            
            results = model.predict(
                source=frame,
                conf=0.75,
                iou=0.5,
                show=False,
                verbose=False,
                imgsz=640,
                device='cpu',
                half=False
            )
            
            annotated = results[0].plot()
            cv2.imshow(f"Monitoreo de {especie_actual.capitalize()}", annotated)
            
            boxes = results[0].boxes
            cantidad = len(boxes)
            
            if cantidad > 0:
                if time.time() - ultimo_envio > tiempo_espera:
                    print(f"🚨 Detectados {cantidad} {especie_actual}")
                    enviar_alerta(especie_actual, cantidad, frame)
                    ultimo_envio = time.time()
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    
    finally:
        liberar_camara(cap, tipo_camara)
        print("👋 Sistema detenido.")

if __name__ == "__main__":
    main()

