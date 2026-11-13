# Puesta en marcha del sistema

Preparación realizada el 12 de noviembre de 2026 para la integración del 13 de noviembre.

El estado actualizado de la integración del 13 de noviembre está en [Continuar en la laptop](CONTINUAR_EN_LAPTOP.md). Las comprobaciones locales de este documento corresponden a la preparación del 12 de noviembre.

## Estado comprobado en esta PC

- Entorno virtual `.venv` con las dependencias de `requirements.txt` instaladas.
- Backend de desarrollo iniciado en `http://127.0.0.1:5000`.
- `GET /config` devuelve HTTP 200 y `{"mode":"tortugas"}`.
- `POST /whatsapp` con el mensaje `menu` devuelve HTTP 200 y las dos especies.
- Existen `modelos/tortugas.pt` y `modelos/gaviotines.pt`.
- Quedan pendientes Railway, credenciales, cámara, instalación en Raspberry y entrega real de WhatsApp.

## Qué utiliza cada parte

| Componente | Función | Lugar de ejecución |
|---|---|---|
| Flask y Gunicorn | Configuración, registro y despacho de alertas | Railway |
| Twilio WhatsApp | Recibir comandos y entregar mensajes | Cuenta Twilio |
| GitHub Contents API | Alojar fotografías accesibles por URL | Repositorio de imágenes |
| OpenCV y Ultralytics YOLO | Capturar y detectar animales | Raspberry Pi con cámara y escritorio gráfico |
| Archivos JSON | Usuarios, preferencias y modo de respaldo | Backend y Raspberry |

El recorrido de una detección es cámara → YOLO → fotografía en GitHub → `/alerta` en Railway → Twilio → WhatsApp. La Raspberry consulta `/config` para elegir el modelo.

## Volver a iniciar el backend local en Windows

Desde PowerShell en la raíz del proyecto, ejecutar lo siguiente cuando el proceso anterior haya terminado.

```powershell
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

Mantener esa terminal abierta. En otra terminal se puede verificar la configuración.

```powershell
Invoke-RestMethod http://127.0.0.1:5000/config
```

Para detener una ejecución en primer plano, pulsar Ctrl+C. La ejecución de preparación se inició en segundo plano y guarda sus registros en `.venv/backend.stdout.log` y `.venv/backend.stderr.log`.

Esta dirección local permite comprobar Flask desde esta PC. Para la integración remota se utilizará el dominio público de Railway.

## Conectar Railway

1. Abrir el servicio existente del proyecto en Railway. Si se necesita crear uno, conectarlo al repositorio que contiene `app.py`.
2. Configurar la instalación con `pip install -r requirements.txt`.
3. Configurar el comando de arranque siguiente.

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
```

4. Completar estas variables en Railway.

| Variable | Valor |
|---|---|
| `TWILIO_ACCOUNT_SID` | Account SID de la cuenta Twilio |
| `TWILIO_AUTH_TOKEN` | Auth Token de la misma cuenta |
| `TWILIO_WHATSAPP_FROM` | Remitente de esa cuenta con formato `whatsapp:+NUMERO` |
| `ALERTA_KEY` | Clave compartida elegida para el sistema |

5. Desplegar y comprobar los logs de inicio de Gunicorn.
6. En Settings → Networking, obtener o generar el dominio público.
7. Abrir `https://DOMINIO-REAL/config` y comprobar que devuelve `mode`.

Guardar el dominio como URL base, sin `/config`, `/alerta` ni barra final. La misma clave `ALERTA_KEY` se configurará en la Raspberry.

Railway documenta el despliegue Flask y la publicación del dominio. [Guía Flask](https://railway.com/guides/flask), [dominio público](https://docs.railway.com/networking/public-networking).

## Reconectar WhatsApp en Twilio

1. Abrir el Sandbox de WhatsApp o el remitente WhatsApp que se utilizaba.
2. Configurar el webhook de mensajes entrantes en `https://DOMINIO-REAL/whatsapp`, con método POST, y guardar.
3. Si se utiliza Sandbox, enviar desde el teléfono el mensaje `join CODIGO-DEL-SANDBOX` al número indicado en la consola. La afiliación al Sandbox vence a los tres días. [Sandbox de Twilio](https://www.twilio.com/docs/whatsapp/sandbox).
4. Tras la confirmación del Sandbox, enviar un segundo mensaje `join` para registrar el teléfono en esta aplicación. Esperar la respuesta «Registro exitoso».
5. Enviar `menu` y después `1` para tortugas o `2` para gaviotines.
6. Consultar nuevamente `/config` y comprobar el modo elegido.

La integración actual envía mensajes de texto libre. Para la demostración, enviar `menu` el mismo día desde cada teléfono destinatario para abrir la ventana de atención de 24 horas. Fuera de esa ventana Twilio requiere una plantilla aprobada para iniciar el envío. [Ventana de mensajería](https://www.twilio.com/docs/api/errors/63016).

El backend guarda usuarios y preferencias en archivos temporales. Después de un redespliegue, comprobar el registro con `join` y volver a seleccionar la especie.

## Preparar GitHub para las fotografías

`utils/github_upload.py` apunta actualmente a `Emmy-Abigail/SISTEMA_MONITOREO`, carpeta `images/capturas`, y construye URLs públicas de la rama `main`.

1. Confirmar que esa cuenta y ese repositorio serán el destino de las imágenes.
2. Preparar un token que tenga acceso a ese repositorio y permiso Contents de escritura. Guardarlo como `GITHUB_TOKEN` en la Raspberry. [Permisos de Contents API](https://docs.github.com/en/rest/repos/contents).
3. Si el destino real cambia, ajustar `REPO_OWNER` y `REPO_NAME` en `utils/github_upload.py` antes de iniciar el detector.
4. Comprobar que una imagen de ese destino abre mediante su URL RAW desde un navegador sin sesión iniciada.

El detector continúa con la notificación cuando obtiene la URL de la fotografía. Una subida fallida interrumpe ese intento de alerta.

## Preparar la Raspberry Pi

Conectar la Raspberry a internet y conectar la cámara. Abrir una terminal dentro de su sesión gráfica. Para entrar por SSH desde otra máquina se necesitarán el usuario y la IP reales.

```bash
ssh USUARIO@IP-DE-LA-RASPBERRY
```

En la Raspberry, desde la raíz de la copia del proyecto, crear el entorno e instalar las dependencias.

```bash
python3 --version
uname -m
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements_raspberry.txt
```

La instalación del detector queda por comprobar en el equipo. La versión de Python y la arquitectura deben ser compatibles con los paquetes fijados en ese archivo. Conservar el entorno anterior si ya funciona y usar su intérprete para la integración.

Definir las tres variables en la misma terminal donde se iniciará el detector.

```bash
export RAILWAY_URL="https://DOMINIO-REAL"
export ALERTA_KEY="CLAVE-COMPARTIDA-CON-RAILWAY"
read -rsp "Token de GitHub: " GITHUB_TOKEN
echo
export GITHUB_TOKEN
```

Sustituir los valores de ejemplo. El código lee variables de entorno directamente. Para repetir una sesión, volver a definirlas antes de arrancar. Un archivo `.env` requiere un mecanismo adicional para cargar sus valores.

Comprobar primero la conexión remota y las bibliotecas.

```bash
curl --fail --max-time 10 "$RAILWAY_URL/config"
python -c "import cv2, requests; from ultralytics import YOLO; print('Dependencias disponibles')"
```

Iniciar el detector desde la raíz mediante el comando siguiente, que permite resolver el paquete `utils`.

```bash
python -m src.detector
```

El programa abre la cámara de índice 0 y muestra una ventana de OpenCV. Para una sesión SSH, ejecutar el detector desde el escritorio de la Raspberry o configurar una sesión con visualización compatible. Pulsar `q` en la ventana para terminar.

## Verificación final del 13 de noviembre

1. Confirmar HTTP 200 y modo válido en el dominio público, ruta `/config`.
2. Enviar `join`, `menu` y la especie desde el teléfono. Confirmar las respuestas del bot.
3. Iniciar el detector y confirmar cámara, modelo cargado y consulta a Railway.
4. Presentar una escena de prueba para provocar una detección real.
5. Comprobar la fotografía en GitHub y abrir su URL RAW.
6. Revisar la respuesta de `/alerta`, incluidos `enviados` y `fallos`.
7. Confirmar en el teléfono la recepción del texto y la imagen.

Las alertas se envían a los teléfonos registrados. El detector puede repetir un intento después de más de 20 segundos con detecciones presentes.

## Resolver problemas durante la integración

| Síntoma | Comprobación |
|---|---|
| `/config` inaccesible | Logs de Railway, dominio público, despliegue y puerto de escucha |
| WhatsApp sin respuesta | Webhook `/whatsapp` con POST y afiliación vigente al Sandbox |
| Error 63015 | Volver a unirse al Sandbox desde el teléfono |
| Error 63016 | Enviar un mensaje al bot para abrir la ventana de atención |
| Respuesta `no_users` | Enviar `join` al bot después de conectar el webhook |
| HTTP 401 en `/alerta` | Igualar `ALERTA_KEY` entre Railway y Raspberry y reiniciar el detector |
| Fallo de subida | Token, permiso Contents, propietario y repositorio configurados |
| `No module named utils` | Ejecutar `python -m src.detector` desde la raíz |
| Cámara sin imagen | Cámara conectada y disponible como índice 0, permisos y uso por otras aplicaciones |
| Fallo de `imshow` | Sesión gráfica disponible para OpenCV |

La integración se considera comprobada cuando llega al teléfono una alerta real con fotografía.
