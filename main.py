from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
import asyncio

# Fake web server for Koyeb
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot Running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)  # Koyeb needs an open port

# Telegram API details
API_ID = 28866244
API_HASH = "e6ade414044776910e7c63ff4643a7b0"
SESSION_NAME = "teleb"

# Channel details
SOURCE_CHANNEL = -1002118541881  
DEST_CHANNEL = -1002613474973   

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    """ Forward new incoming messages from the source channel. """
    if event.message.media:
        try:
            await event.message.forward_to(DEST_CHANNEL)
            print(f"✅ Forwarded new message: {event.message.id}")
        except Exception as e:
            print(f"⚠️ Error forwarding new message: {e}")

async def main():
    """ Start the bot """
    print("🚀 Starting userbot...")
    print("👀 Listening for new messages...")
    await client.run_until_disconnected()

# Run Flask in a separate thread
Thread(target=run_flask).start()

with client:
    client.loop.run_until_complete(main())
