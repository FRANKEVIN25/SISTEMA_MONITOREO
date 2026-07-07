<!--
  Suggested GitHub repo description (keep the current one, it's good):
  "Automated hatching-monitoring system for sea turtle and Peruvian tern nests — YOLO on Raspberry Pi with real-time WhatsApp alerts."
  Suggested topics: yolo, computer-vision, raspberry-pi, twilio, whatsapp, flask, conservation, edge-ai
-->

# Wildlife Hatching Monitor 🐢

**Automated monitoring system for sea turtle and Peruvian tern (gaviotín peruano) nests**, built to reduce hatchling mortality on Peru's northern coast. When eggs begin to hatch, conservation volunteers receive an instant **WhatsApp alert with a photo** — so they can intervene in time.

The problem: hatching happens unpredictably, often at night, and volunteers can't watch every nest. Late detection is one of the main causes of hatchling death. This system watches for them, 24/7.

## How it works

```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│   Raspberry Pi       │  HTTPS  │   Flask backend       │  Twilio │   Volunteers     │
│   + camera           │────────▶│   (Railway)           │────────▶│   WhatsApp       │
│   YOLO detection     │  alert  │   subscriptions +     │  alert  │   photo + msg    │
│   (edge inference)   │         │   alert dispatch      │         │                  │
└─────────────────────┘         └──────────────────────┘         └─────────────────┘
```

1. **Edge detection** — a Raspberry Pi with a camera runs a custom-trained **YOLO** model (Ultralytics + OpenCV) directly on-device, watching the nest.
2. **Species modes** — two fine-tuned models are included (`modelos/tortugas.pt`, `modelos/gaviotines.pt`); the active species is configured remotely through the backend's `/config` endpoint.
3. **Alert pipeline** — on detection, the frame is captured, uploaded for hosting, and an authenticated alert (protected by a shared secret) is sent to the cloud backend.
4. **WhatsApp delivery** — the Flask backend, deployed on **Railway**, uses the **Twilio WhatsApp API** to notify every subscribed volunteer. Volunteers register themselves by messaging the bot on WhatsApp.

## Tech stack

| Component | Technology |
|---|---|
| Object detection | Ultralytics YOLO (custom-trained), OpenCV |
| Edge device | Raspberry Pi (Python) |
| Backend | Flask + Gunicorn, deployed on Railway |
| Messaging | Twilio WhatsApp API (webhook + REST) |
| Storage | JSON state (subscribers, config), image hosting via GitHub |

## Project structure

```
├── app.py                     # Flask backend: WhatsApp webhook, /alerta, /config
├── src/detector.py            # Raspberry Pi: camera loop + YOLO inference
├── utils/
│   ├── send_alert.py          # Capture, upload and dispatch alerts
│   └── github_upload.py       # Image hosting
├── modelos/
│   ├── tortugas.pt            # Sea turtle model
│   └── gaviotines.pt          # Peruvian tern model
├── requirements.txt           # Backend dependencies
├── requirements_raspberry.txt # Edge device dependencies
└── Procfile                   # Railway deployment
```

## Running it

**Backend (Railway or local):**
```bash
pip install -r requirements.txt
export TWILIO_ACCOUNT_SID=...
export TWILIO_AUTH_TOKEN=...
export TWILIO_WHATSAPP_FROM=whatsapp:+1415XXXXXXX
export ALERTA_KEY=your_secret
gunicorn app:app --timeout 120
```

**Detector (Raspberry Pi):**
```bash
pip install -r requirements_raspberry.txt
export RAILWAY_URL=https://your-backend.up.railway.app
export ALERTA_KEY=your_secret
python src/detector.py
```

## Context

Developed as part of an engineering project at **Universidad Peruana Cayetano Heredia (UPCH)**, inspired by **SDG 14: Life Below Water**. The course documentation and design process live in [GRUPO_4_PROYECTOS](https://github.com/FRANKEVIN25/GRUPO_4_PROYECTOS).

## Author

**Frank Jáuregui** — [LinkedIn](https://linkedin.com/in/frank-jauregui) · [GitHub](https://github.com/FRANKEVIN25)
