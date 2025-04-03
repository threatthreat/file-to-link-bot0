import asyncio
import json
import hashlib
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# API Details
API_ID = 29010066  
API_HASH = "2e0d5a624f4eb3991826a9abe13c78b7"
SESSION_STRING = "1BVtsOKEBu3BMRGFVb4veoTMMXd5FB1Xy0fOHZLUJtEbkJk27i0nCXG-R9oBgGYK1pBwsQYmmme-ZnPekM2EG_e-2rDYHAvy4m98jcglQ6RhkF01Kt6nCkgUq8jF5l2KQM1qY4vjOwGBHVYofT1X2vLeDoWHyiuumQezY_IWR9E9NTvUNIEzRIAXVSyk_uiuz-6FfeqI1_hW-8Rsg6RrEN5afe56Ww5lBUhEw8LxxKETb9xUV4Y8gfcqJhJqjOR4IV4kviz9dtPiTBBDg8k-HbRWv5wLTkSAbUCC8gpYRcmIE21oXnmu687r42iYYCSSGiqrWmJrqcgCKtlrjsPGYyfzXf-EmH6E="

# Channel Details
SOURCE_CHANNEL = -1002118541881  
DEST_CHANNEL = -1002621781430    

# Load previously forwarded files
FORWARDED_FILES_DB = "forwarded_files.json"
try:
    with open(FORWARDED_FILES_DB, "r") as f:
        forwarded_files = set(json.load(f))
except FileNotFoundError:
    forwarded_files = set()

# Initialize Telegram Client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Function to get file hash
def get_file_hash(message):
    if message.file:
        return hashlib.md5(str(message.file.id).encode()).hexdigest()
    return None

# Function to save forwarded files
def save_forwarded_files():
    with open(FORWARDED_FILES_DB, "w") as f:
        json.dump(list(forwarded_files), f)

async def forward_messages():
    """ Forward only .mp4 and .mkv files, avoiding duplicates """
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media and message.file:
            if message.file.ext.lower() in [".mp4", ".mkv"]:
                file_hash = get_file_hash(message)
                if file_hash and file_hash not in forwarded_files:
                    try:
                        await message.forward_to(DEST_CHANNEL)
                        forwarded_files.add(file_hash)
                        save_forwarded_files()
                        print(f"✅ Forwarded: {message.id} | Total: {len(forwarded_files)}")
                        await asyncio.sleep(5)  # Fixed delay of 5 seconds
                    except Exception as e:
                        print(f"⚠️ Error forwarding {message.id}: {e}")
                        await asyncio.sleep(10)  # Short wait before retry

@client.on(events.NewMessage(chats=[SOURCE_CHANNEL]))
async def new_message_handler(event):
    """ Handle new messages only for .mp4 and .mkv """
    if event.message.media and event.message.file:
        if event.message.file.ext.lower() in [".mp4", ".mkv"]:
            file_hash = get_file_hash(event.message)
            if file_hash and file_hash not in forwarded_files:
                try:
                    await event.message.forward_to(DEST_CHANNEL)
                    forwarded_files.add(file_hash)
                    save_forwarded_files()
                    print(f"✅ Forwarded new message: {event.message.id}")
                    await asyncio.sleep(5)
                except Exception as e:
                    print(f"⚠️ Error forwarding new message: {e}")
                    await asyncio.sleep(10)

async def main():
    await client.start()
    print("🚀 Userbot started! Listening for new messages...")
    await asyncio.gather(forward_messages(), client.run_until_disconnected())

# Flask App for UptimeRobot
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
