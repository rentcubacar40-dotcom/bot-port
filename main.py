import requests
import time
import os
import platform
import socket
import datetime
import logging
import threading
import psutil

# ✅ VERSIÓN CORREGIDA
BOT_VERSION = "FIXED-" + datetime.datetime.now().strftime("%m%d%H%M")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# ✅ FUNCIONES CORREGIDAS (sin self)
def _bytes_to_mb(bytes_value):
    """Convertir bytes a MB"""
    return round(bytes_value / (1024 * 1024), 2)

def _bytes_to_gb(bytes_value):
    """Convertir bytes a GB"""
    return round(bytes_value / (1024 * 1024 * 1024), 2)

def keep_alive():
    while True:
        logger.info(f"❤️ Worker v{BOT_VERSION} activo")
        time.sleep(1800)

def send_message(chat_id, text):
    try:
        response = requests.post(
            f"{API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error enviando mensaje: {e}")
        return False

def get_detailed_server_info():
    """INFORMACIÓN COMPLETA DEL SERVIDOR - VERSIÓN CORREGIDA"""
    try:
        hostname = socket.gethostname()
        system = platform.system()
        release = platform.release()
        architecture = platform.machine()
        
        # Información de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Información de memoria
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Información de red
        try:
            ip_local = socket.gethostbyname(hostname)
        except:
            ip_local = "No disponible"
        
        # Información de procesos
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Tiempo
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        current_time = datetime.datetime.now()
        
        # ✅ CORREGIDO: Usar las funciones directamente, sin self
        info = (
            f"🖥️ *INFORMACIÓN DETALLADA - v{BOT_VERSION}*\n\n"
            
            "🔧 *SISTEMA:*\n"
            f"• Hostname: `{hostname}`\n"
            f"• SO: `{system} {release}`\n"
            f"• Arquitectura: `{architecture}`\n"
            f"• IP Local: `{ip_local}`\n\n"
            
            "⚡ *CPU:*\n"
            f"• Uso: `{cpu_percent}%`\n"
            f"• Núcleos: `{cpu_count}`\n"
            f"• Frecuencia: `{cpu_freq.current if cpu_freq else 'N/A'} MHz`\n\n"
            
            "💾 *MEMORIA:*\n"
            f"• Usada: `{memory.percent}%`\n"
            f"• Total: `{_bytes_to_gb(memory.total)} GB`\n"
            f"• Disponible: `{_bytes_to_gb(memory.available)} GB`\n\n"
            
            "💽 *DISCO:*\n"
            f"• Usado: `{disk.percent}%`\n"
            f"• Total: `{_bytes_to_gb(disk.total)} GB`\n"
            f"• Libre: `{_bytes_to_gb(disk.free)} GB`\n\n"
            
            "📊 *PROCESO:*\n"
            f"• Memoria Bot: `{_bytes_to_mb(process_memory.rss)} MB`\n"
            f"• Uptime: `{str(uptime).split('.')[0]}`\n"
            f"• Hora: `{current_time.strftime('%H:%M:%S')}`\n\n"
            
            "✅ *BOT CON INFORMACIÓN COMPLETA*"
        )
        return info
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def process_message(chat_id, text):
    logger.info(f"Procesando: {text} - v{BOT_VERSION}")
    
    if text == "/start":
        welcome_msg = (
            f"🤖 *BOT CHOREO DETALLADO - v{BOT_VERSION}*\n\n"
            "📋 *COMANDOS:*\n"
            "• `/info` - Información COMPLETA del servidor\n"
            "• `/status` - Estado rápido\n\n"
            "🔧 *Versión corregida y funcionando*"
        )
        send_message(chat_id, welcome_msg)
        
    elif text == "/info":
        server_info = get_detailed_server_info()
        send_message(chat_id, server_info)
        
    elif text == "/status":
        quick_info = (
            f"📊 *ESTADO RÁPIDO - v{BOT_VERSION}*\n"
            f"• Hostname: `{socket.gethostname()}`\n"
            f"• CPU: `{psutil.cpu_percent()}%`\n"
            f"• Memoria: `{psutil.virtual_memory().percent}%`\n"
            f"• Hora: `{datetime.datetime.now().strftime('%H:%M:%S')}`\n"
            "✅ *Sistema estable*"
        )
        send_message(chat_id, quick_info)
        
    else:
        send_message(chat_id, 
            f"❌ Comando no reconocido\n\n"
            f"Usa `/info` para información completa\n"
            f"*Versión: {BOT_VERSION}*"
        )

def main():
    logger.info(f"🚀 Iniciando Bot v{BOT_VERSION} - CÓDIGO CORREGIDO")
    
    if not TOKEN:
        logger.error("❌ TELEGRAM_TOKEN no configurado")
        return
    
    # Iniciar keep-alive
    threading.Thread(target=keep_alive, daemon=True).start()
    
    # Bucle principal
    offset = None
    while True:
        try:
            params = {"timeout": 25, "offset": offset}
            response = requests.get(f"{API_URL}/getUpdates", params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    updates = data.get("result", [])
                    
                    for update in updates:
                        if "message" in update:
                            chat_id = update["message"]["chat"]["id"]
                            text = update["message"].get("text", "").lower().strip()
                            process_message(chat_id, text)
                        
                        offset = update["update_id"] + 1
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error en polling: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
