import os, json, asyncio
from flask import Flask, request, abort
from telegram import Update, Bot
from telegram.ext import CommandHandler, Dispatcher

# Variables de entorno
BOT_TOKEN = os.environ.get("BOT_TOKEN")
PUBLIC_URL = os.environ.get("PUBLIC_URL")
OWNER_ID = os.environ.get("OWNER_ID")  # tu ID numérico de Telegram
ALLOWED_ENV = os.environ.get("ALLOWED_USERS", "")  # opcional, "@usuario1,@usuario2"

if not BOT_TOKEN or not PUBLIC_URL or not OWNER_ID:
    raise RuntimeError("Define BOT_TOKEN, PUBLIC_URL y OWNER_ID en variables de entorno")

app = Flask(__name__)
bot = Bot(BOT_TOKEN)
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"

ALLOWED_FILE = "allowed.json"

# Cargar lista de usuarios permitidos
def load_allowed():
    allowed = set()
    if ALLOWED_ENV:
        for u in ALLOWED_ENV.split(","):
            u = u.strip()
            if u:
                allowed.add(u)
    if os.path.exists(ALLOWED_FILE):
        try:
            with open(ALLOWED_FILE, "r") as f:
                data = json.load(f)
                for u in data.get("allowed", []):
                    allowed.add(u)
        except:
            pass
    return allowed

def save_allowed(allowed_set):
    try:
        with open(ALLOWED_FILE, "w") as f:
            json.dump({"allowed": list(allowed_set)}, f)
    except:
        pass

allowed = load_allowed()

# Verificar si el usuario puede usar el bot
def is_allowed(username, user_id_str):
    if username and username in allowed:
        return True
    if str(user_id_str) == str(OWNER_ID):
        return True
    return False

# Comando /start
async def handle_start(update, context):
    msg = update.message
    from_user = msg.from_user
    username = ("@" + from_user.username) if from_user.username else ""
    if not is_allowed(username, from_user.id):
        await msg.reply_text("No tienes permiso para usar este bot.")
        return
    await msg.reply_text("¡Hola! Bienvenido al bot. Usa /allow @usuario para dar permisos (si eres el owner).")

# Comando /allow @usuario
async def handle_allow(update, context):
    msg = update.message
    from_user = msg.from_user
    if str(from_user.id) != str(OWNER_ID):
        await msg.reply_text("Solo el propietario puede dar permisos.")
        return
    parts = msg.text.split()
    if len(parts) < 2:
        await msg.reply_text("Uso: /allow @nombre_usuario")
        return
    user_to = parts[1].strip()
    if not user_to.startswith("@"):
        await msg.reply_text("El usuario debe empezar con @. Ej: /allow @pepe")
        return
    allowed.add(user_to)
    save_allowed(allowed)
    await msg.reply_text(f"Usuario {user_to} agregado a la lista permitida.")

# Endpoint webhook
@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dp = Dispatcher(bot=bot, update_queue=None, use_context=True)
        dp.add_handler(CommandHandler("start", lambda u,c: asyncio.run(handle_start(u,c))))
        dp.add_handler(CommandHandler("allow", lambda u,c: asyncio.run(handle_allow(u,c))))
        dp.process_update(update)
        return "OK"
    else:
        abort(403)

if __name__ == "__main__":
    webhook_url = PUBLIC_URL + WEBHOOK_PATH
    bot.delete_webhook(drop_pending_updates=True)
    bot.set_webhook(webhook_url)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
