import asyncio
import hashlib
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# API Details
API_ID = 29010066  
API_HASH = "2e0d5a624f4eb3991826a9abe13c78b7"
SESSION_STRING = "1BVtsOKEBu3BMRGFVb4veoTMMXd5FB1Xy0fOHZLUJtEbkJk27i0nCXG-R9oBgGYK1pBwsQYmmme-ZnPekM2EG_e-2rDYHAvy4m98jcglQ6RhkF01Kt6nCkgUq8jF5l2KQM1qY4vjOwGBHVYofT1X2vLeDoWHyiuumQezY_IWR9E9NTvUNIEzRIAXVSyk_uiuz-6FfeqI1_hW-8Rsg6RrEN5afe56Ww5lBUhEw8LxxKETb9xUV4Y8gfcqJhJqjOR4IV4kviz9dtPiTBBDg8k-HbRWv5wLTkSAbUCC8gpYRcmIE21oXnmu687r42iYYCSSGiqrWmJrqcgCKtlrjsPGYyfzXf-EmH6E="

# Channel details
SOURCE_CHANNEL = -1002118541881  
DEST_CHANNEL = -1002621781430    

# Initialize Telegram Client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# File to store forwarded file hashes
HASH_FILE = "forwarded_files.json"

def load_forwarded_files():
    """ Load previously forwarded file hashes from JSON file. """
    try:
        with open(HASH_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_forwarded_file(file_hash):
    """ Save a new forwarded file hash to JSON file. """
    forwarded_files.add(file_hash)
    with open(HASH_FILE, "w") as f:
        json.dump(list(forwarded_files), f)

def get_file_hash(message):
    """ Generate a hash for the file to detect duplicates. """
    if message.file:
        return hashlib.md5(str(message.file.id).encode()).hexdigest()
    return None

# Load previous forwarded file hashes
forwarded_files = load_forwarded_files()

async def forward_messages():
    """ Forward messages without forwarding duplicates. """
    while True:
        try:
            async for message in client.iter_messages(SOURCE_CHANNEL):
                if message.media:
                    file_hash = get_file_hash(message)
                    if file_hash and file_hash not in forwarded_files:
                        try:
                            await message.forward_to(DEST_CHANNEL)
                            save_forwarded_file(file_hash)
                            print(f"✅ Forwarded: {message.id}")
                            await asyncio.sleep(5)
                        except Exception as e:
                            print(f"⚠️ Error forwarding {message.id}: {e}")
                            await asyncio.sleep(20)
        except Exception as e:
            print(f"⚠️ Disconnected! Reconnecting in 10 sec... Error: {e}")
            await asyncio.sleep(10)

@client.on(events.NewMessage(chats=[SOURCE_CHANNEL]))
async def new_message_handler(event):
    """ Handle new messages and avoid duplicates. """
    if event.message.media:
        file_hash = get_file_hash(event.message)
        if file_hash and file_hash not in forwarded_files:
            try:
                await event.message.forward_to(DEST_CHANNEL)
                save_forwarded_file(file_hash)
                print(f"✅ Forwarded new message: {event.message.id}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"⚠️ Error forwarding new message: {e}")
                await asyncio.sleep(20)

async def main():
    """ Start bot with auto-reconnect. """
    while True:
        try:
            print("🚀 Starting userbot...")
            await client.start()
            print("✅ Userbot started! Listening for new messages...")
            await asyncio.gather(forward_messages(), client.run_until_disconnected())
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting in 10 sec...")
            await asyncio.sleep(10)

# Flask App for Uptime Monitoring
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask in a separate thread
threading.Thread(target=run_flask, daemon=True).start()

# Start the bot
client.loop.run_until_complete(main())
