# Dashboard propio y cámara de PC

El dashboard está integrado en Flask, en `/` y `/dashboard`. Conserva las rutas `/config`, `/whatsapp` y `/alerta`. El detector de PC envía capturas JPEG y detecciones directamente a este backend.

## Ejecutar en Windows

Desde la carpeta del proyecto, preparar el entorno. Para esta prueba se utiliza CPU.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements_pc.txt
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

Abrir `http://127.0.0.1:5000` en el navegador. En otra terminal, ejecutar el monitor.

```powershell
.\.venv\Scripts\python.exe -m src.monitor_pc --url http://127.0.0.1:5000
```

Seleccionar la especie en el dashboard y pulsar Iniciar monitoreo. Detener pausa la inferencia. La cámara continúa mostrando imágenes mientras el proceso está abierto. Pulsar `q` en la ventana de OpenCV para cerrar el monitor y liberar la cámara.

La vista del dashboard es la última captura enviada por el dispositivo, actualizada cada cinco segundos. El conteo acumula los objetos de cada evento registrado. Un mismo individuo puede aparecer en eventos sucesivos.

## Conectar la PC a Railway

Publicar este código en el servicio de la cuenta del usuario. El servicio instala `requirements.txt` y ejecuta el Procfile. Las dependencias de cámara y YOLO se instalan en la PC.

Conservar las variables Twilio y ALERTA_KEY ya configuradas. En el proyecto Railway, agregar un volumen al servicio con ruta `/data`. Railway proporciona `RAILWAY_VOLUME_MOUNT_PATH` y el backend utiliza esa ruta automáticamente para SQLite, usuarios y preferencias. Usar una sola réplica del servicio con este almacenamiento. [Volúmenes de Railway](https://docs.railway.com/volumes).

Si el volumen está ausente, el dashboard informa que el historial es temporal. En local, los datos quedan en `.runtime/`. `MONITOREO_DATA_DIR` permite elegir otra carpeta. Para recuperar los JSON anteriores, el backend copia los archivos del directorio temporal si los nuevos todavía no existen.

Abrir el dominio de Railway en el navegador. En Clave de control, introducir el valor de ALERTA_KEY. Ese mismo valor se introduce cuando lo solicite el monitor de PC.

```powershell
.\.venv\Scripts\python.exe -m src.monitor_pc --url https://sistemamonitoreo-production-8883a6d5.up.railway.app
```

El monitor lee ALERTA_KEY del entorno o la solicita de forma oculta al usar un servidor remoto. La clave se envía exclusivamente al backend indicado en `--url`. La PC debe permanecer encendida, conectada a internet y con el proceso abierto.

Para solicitar también las alertas a WhatsApp, agregar `--whatsapp`. El backend enviará a los teléfonos previamente registrados mediante `join`. La prueba de alertas depende de la configuración y disponibilidad de Twilio, de la afiliación al Sandbox y de su ventana de mensajería.

```powershell
.\.venv\Scripts\python.exe -m src.monitor_pc --url https://sistemamonitoreo-production-8883a6d5.up.railway.app --whatsapp
```

Las nuevas capturas se almacenan en el backend y se sirven por URL pública, al igual que el dashboard. El historial muestra los cien eventos más recientes del filtro. Los conteos y el gráfico incluyen todos los eventos del período seleccionado.

## Comprobar el funcionamiento

1. Abrir el dashboard y comprobar Servidor conectado.
2. Ejecutar el monitor y comprobar Cámara conectada.
3. Seleccionar tortugas o gaviotines e iniciar.
4. Presentar una escena con la especie seleccionada. El umbral de confianza es 0.75.
5. Comprobar la captura, la cantidad y el gráfico. Los intentos de registro se separan por veinte segundos cuando hay detecciones.
6. Pulsar Detener y comprobar el cambio a espera.

Las detecciones usan un UUID que permite reintentar su registro sin duplicarlas. El agente conserva una detección pendiente en memoria y reintenta cada cinco segundos mientras sigue ejecutándose. El envío opcional a WhatsApp se solicita una vez tras registrar cada evento.

## Verificaciones pendientes del entorno remoto

Antes de publicar, confirmar en Railway el repositorio, la rama y el commit del servicio. En la integración anterior se observó un menú ÑAWI APU distinto del código de esta copia. El despliegue de esta rama utiliza el menú de WhatsApp de `app.py` y añade el dashboard propio.

Para continuar el contexto general, consultar `docs/CONTINUAR_EN_LAPTOP.md`.
