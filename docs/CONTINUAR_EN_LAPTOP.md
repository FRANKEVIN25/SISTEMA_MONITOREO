# Continuar la integración desde la laptop

Actualizado el 13 de noviembre de 2026, hora de Perú.

## Actualización del dashboard propio

El usuario eligió crear una página web propia integrada con Railway. La implementación está en `/` y `/dashboard`, con control de especie, última imagen de la cámara, conteos e historial SQLite. El monitor para PC es `python -m src.monitor_pc`. La instalación y conexión están en [Dashboard y cámara de PC](DASHBOARD.md).

La cámara de esta PC entregó imágenes de 640 × 480. Ambos modelos cargaron y ejecutaron inferencia. El agente transmitió una captura al backend local y se verificó su respuesta HTTP. La recepción de una detección real de fauna, la publicación de esta versión en el servicio correcto de Railway y el volumen remoto requieren completar la integración.

## Punto donde quedó la sesión

El usuario terminó de configurar las cuatro variables del servicio Railway y confirmó que estaban listas. El siguiente paso pendiente es esperar el despliegue activo, enviar `menu` desde el teléfono al Sandbox correcto y revisar el resultado. Todavía falta confirmar que el menú llegue realmente a WhatsApp.

## Direcciones que se deben conservar

| Recurso | Dirección o dato |
|---|---|
| Repositorio de trabajo | https://github.com/FRANKEVIN25/SISTEMA_MONITOREO |
| Rama de trabajo | `main` |
| Proyecto Railway visto en la sesión | `intuitive-celebration` |
| Entorno y servicio | `production` / `SISTEMA_MONITOREO` |
| URL base del backend | https://sistemamonitoreo-production-8883a6d5.up.railway.app |
| Consulta de configuración | https://sistemamonitoreo-production-8883a6d5.up.railway.app/config |
| Webhook de WhatsApp | https://sistemamonitoreo-production-8883a6d5.up.railway.app/whatsapp |
| Número del Sandbox clásico vinculado | `+1 415 523 8886` |
| Instancia Grafana Cloud | https://frankjauregui.grafana.net |
| Dashboard Grafana | Detección de Tortugas y Gaviotines |

## Estado comprobado y pendiente

| Parte | Estado al terminar |
|---|---|
| Railway | Servicio creado en la cuenta del usuario y dominio público generado. |
| Variables Railway | Usuario confirmó que completó las cuatro variables. Falta comprobar que el despliegue activo las incorporó y que Twilio acepta las credenciales. |
| `GET /config` público | Comprobado por terminal con HTTP 200 y `{"mode":"detenido"}`. |
| `POST /whatsapp` público | Comprobado con `Body=menu`, sin datos telefónicos. Respondió HTTP 200 y XML TwiML con el menú ÑAWI APU. |
| Afiliación al Sandbox | Confirmada mediante respuesta de Twilio al teléfono del usuario. |
| Recepción del menú en el teléfono | Pendiente. La última captura mostraba `menu` enviado sin respuesta. |
| Error de Twilio | Se observó `11321 — Misconfigured webhook`, el 13 de noviembre a las 14:18 UTC, equivalente a las 09:18 de Perú. Falta comprobar si persiste después de los últimos cambios. |
| Raspberry y cámara | Instalación, conexión, inferencia y envío real pendientes. |
| GitHub para imágenes | La copia local todavía apunta a `Emmy-Abigail/SISTEMA_MONITOREO`. Falta migrar a la cuenta del usuario y probar la subida. |
| Grafana | Dashboard localizado en Cloud. Paneles con errores. Fuente de datos y proceso que los alimenta pendientes de identificar. |

## Configuración guardada en Railway

En Railway → servicio `SISTEMA_MONITOREO` → Variables quedaron estos nombres.

| Variable | Procedencia y uso |
|---|---|
| `TWILIO_ACCOUNT_SID` | Account SID de la cuenta Twilio del usuario. |
| `TWILIO_AUTH_TOKEN` | Auth Token de la misma cuenta. |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` |
| `ALERTA_KEY` | Clave elegida por el usuario. Debe coincidir con la que se configure en el detector. |

Los valores privados deben recuperarse desde Railway o el gestor de contraseñas del usuario. Estos documentos contienen nombres y direcciones de conexión. El entorno virtual de esta PC y las variables de su terminal se recrean en la laptop cuando hagan falta.

## Retomar primero la prueba de WhatsApp

1. Entrar en Railway con la cuenta del usuario, abrir el servicio y comprobar Deployments → Active. Aplicar los cambios pendientes si los hay.
2. Entrar en la misma cuenta de Twilio que posee el Sandbox. El nombre visto fue `My First Twilio Account`.
3. Abrir la consola clásica en https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn. Si abre SMS, elegir Messaging → Try it out → Send a WhatsApp message.
4. En Sandbox settings, comprobar que `When a message comes in` contiene exactamente la dirección siguiente.

```text
https://sistemamonitoreo-production-8883a6d5.up.railway.app/whatsapp
```

5. Seleccionar POST y pulsar Save. Recargar y confirmar que se conservó la URL completa.
6. Desde el teléfono afiliado, enviar `menu` al `+1 415 523 8886`.
7. Si llega el menú, seguir las opciones ofrecidas. Comprobar `/config` tras seleccionar una especie.
8. Si sigue sin responder, abrir Monitor → Logs → Errors → Error logs y examinar el evento más reciente, incluidos los detalles de la URL y de la solicitud. Revisar también los logs de Railway a la misma hora.

El error 11321 indica una URL de webhook inválida o mal configurada. El endpoint público respondió correctamente a la prueba directa, por lo que hay que inspeccionar la URL efectiva que usa Twilio. Todavía no se obtuvo el detalle del evento. [Error 11321](https://www.twilio.com/docs/api/errors/11321).

La consola nueva `1console.twilio.com` ofrecía otro entorno Tryout, con número `+1 737 250 8034` y respuesta automática de demostración. La sesión de integración continuó con el Sandbox clásico `+1 415 523 8886`. Usar este último para las pruebas del webhook descrito aquí.

El teléfono ya se afilió al Sandbox. Si la afiliación vence, abrir su pestaña Sandbox y usar el código join que muestre en ese momento. La afiliación dura tres días. Enviar un mensaje al bot también abre la ventana de atención de 24 horas para los mensajes libres. [Sandbox de Twilio](https://www.twilio.com/docs/whatsapp/sandbox).

El menú se devuelve como respuesta TwiML al webhook entrante. Las alertas automáticas llaman a la API REST y necesitan las credenciales Twilio configuradas en el backend.

## Diferencia entre el despliegue y esta copia del código

El endpoint público probado devolvió un menú ÑAWI APU con cinco opciones, incluidas amenazas, detener y dashboard. También devolvió `mode=detenido`.

La copia local revisada y la rama remota `main` consultada durante la preparación estaban en el commit `ef26259`. Su código presenta un menú más simple y el detector intenta cargar un archivo de modelo según el modo recibido. Esta diferencia requiere identificar el repositorio, la rama y el commit que realmente despliega Railway antes de cambiar código o forzar un redespliegue.

En Railway → Settings → Source, anotar el propietario y repositorio conectado, la rama y el commit del último deployment. Compararlos con `FRANKEVIN25/SISTEMA_MONITOREO`, rama `main`. Publicar documentación en este repositorio puede iniciar un despliegue si Railway tiene activado el despliegue automático.

Antes de iniciar el detector, comprobar cómo maneja la versión efectiva el estado `detenido`. La copia local revisada intentaría cargar `modelos/detenido.pt`, que no está entre los dos modelos disponibles. Seleccionar una especie y confirmar el modo devuelto forma parte de la prueba pendiente.

## Preparar la laptop

Para usar las consolas de Railway, Twilio y Grafana basta el navegador. Para editar o ejecutar el backend local, instalar Git y Python y clonar el repositorio.

```powershell
git clone https://github.com/FRANKEVIN25/SISTEMA_MONITOREO.git
cd SISTEMA_MONITOREO
```

Si ya existe una copia local sin cambios pendientes, actualizarla desde su carpeta.

```powershell
git pull --ff-only origin main
```

Abrir primero `docs/CONTINUAR_EN_LAPTOP.md` en VS Code. Para preparar el backend local, ejecutar lo siguiente.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

El backend local quedará en `http://127.0.0.1:5000`. El webhook de Twilio sigue utilizando el dominio público de Railway. Para detener Flask en la terminal, pulsar Ctrl+C.

En esta PC se instalaron las dependencias del backend y `pip check` no reportó incompatibilidades. La instalación debe comprobarse de nuevo en la laptop. Las dependencias del detector se instalarán y comprobarán en el equipo que ejecutará la cámara.

## Próxima sesión con Raspberry y fotografías

1. Confirmar usuario SSH, dirección IP, acceso a internet y cámara conectada.
2. Recuperar la versión del detector que corresponda con el backend efectivo.
3. Comprobar los modelos `modelos/tortugas.pt` y `modelos/gaviotines.pt`.
4. Instalar y verificar `requirements_raspberry.txt` en un entorno compatible con Python y la arquitectura del equipo.
5. Configurar `RAILWAY_URL` con la URL base de este documento, `ALERTA_KEY` con la misma clave de Railway y `GITHUB_TOKEN` con acceso al repositorio de fotografías.
6. Cambiar el propietario y repositorio de imágenes al destino elegido en la cuenta del usuario. Comprobar permisos de escritura y acceso público a la URL RAW de una fotografía.
7. Ejecutar desde la raíz con `python -m src.detector`, en una sesión gráfica compatible con OpenCV.
8. Confirmar una detección, una subida de imagen y la recepción del WhatsApp con fotografía.

## Próxima sesión con Grafana

1. Entrar en https://frankjauregui.grafana.net.
2. Abrir Connections → Data sources y anotar tipo, nombre y destino de la fuente que usan los paneles. Mantener privadas sus credenciales.
3. Abrir el error de un panel y registrar el mensaje completo.
4. Cambiar el rango del dashboard a Last 24 hours. La captura inicial terminaba el 1 de enero de 2026, anterior a las pruebas actuales.
5. Identificar dónde se guardan las detecciones y qué proceso las envía. En la copia local revisada no se encontró integración con Grafana, InfluxDB, Prometheus ni MQTT.
6. Reconectar y probar la fuente existente una vez identificada.

## Documentación adicional

- `docs/PUESTA_EN_MARCHA.md` contiene los comandos de instalación y diagnóstico general.
- `docs/ARQUITECTURA_SOFTWARE.md` describe la copia local revisada antes de esta integración.

## Mensaje para continuar con Codex en la laptop

```text
Continuemos la integración de SISTEMA_MONITOREO. Lee primero
docs/CONTINUAR_EN_LAPTOP.md y las instrucciones AGENTS.md que correspondan.
Las variables de Railway ya fueron completadas por mí. Falta verificar que
WhatsApp reciba el menú. El último error observado fue Twilio 11321.
Comprueba la fuente real desplegada en Railway porque el menú público y
el modo detenido difieren de la copia del código revisada. Después hay que
conectar Raspberry, fotografías en mi GitHub y la fuente existente de Grafana.
```
