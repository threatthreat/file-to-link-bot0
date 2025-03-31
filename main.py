from flask import Flask
import threading
from telethon import TelegramClient, events
import asyncio
import os

# Load API details
API_ID = int(os.getenv("API_ID", 28866244))
API_HASH = os.getenv("API_HASH", "e6ade414044776910e7c63ff4643a7b0")
SESSION_STRING = "1BVtsOHcBu2KmILIwVTdhfIyrCxx90tjXlMkXHDsTGroLTPVYJCw0iHMvD8meJG7e2mPXD8I2SNL7PvgJjvzU7P31ku1ERBWuQorVJTDm6JzHipPGZt6WUdqS9bFicN2nkZrcx9zchGDiEIEzjDnEjV_y4EOe2QT3_gGAfjUxsZsOaHpV_eefyYX8IgT4LL5djWp_HqgFzUM3OEe4iVCvKMTOaiVr6mXb4hPLNBe-OZsXXJeNMIW5aFfFOo4sQRLR1ni9i0Hshh5nGNVjoi9SMWEEsHCWzWlnHciLSDfhGyNxvmaXR8sBTFwZAoNhwBHYGgRTXIYkSUo9bX5tA7hkbqekKX9LYpE="  # Your session string
SOURCE_CHANNEL = -1002118541881
DEST_CHANNEL = -1002696495424

client = TelegramClient("bot", API_ID, API_HASH).start(session_string=SESSION_STRING)

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

async def forward_all_messages():
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media and message.file and message.file.ext.lower() in [".mp4", ".mkv"]:
            try:
                await message.forward_to(DEST_CHANNEL)
                print(f"✅ Forwarded: {message.id}")
                await asyncio.sleep(2.5)  # Safe delay
            except Exception as e:
                print(f"⚠️ Error forwarding {message.id}: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    if event.message.media and event.message.file and event.message.file.ext.lower() in [".mp4", ".mkv"]:
        try:
            await event.message.forward_to(DEST_CHANNEL)
            print(f"✅ Forwarded new message: {event.message.id}")
        except Exception as e:
            print(f"⚠️ Error forwarding new message: {e}")

async def main():
    print("🚀 Starting userbot...")
    await forward_all_messages()
    await client.run_until_disconnected()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
