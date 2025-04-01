from telethon import TelegramClient, events
import asyncio
import os
import hashlib
from telethon.sessions import StringSession
from flask import Flask
import threading

# API Details
API_ID = 28866244  # Ensure it's an integer
API_HASH = "e6ade414044776910e7c63ff4643a7b0"
SESSION_STRING = "1BVtsOKYBu2NOfK00wpq9jyAdscYD8L0cjt27uMTLhyiiC1T5y4QXeoT7tmzJ8CweFxfQVCQCWjBAEDlTBZPjpUJ1aAZrt_IhaZx44ZPVdHyp19afL6EgMz9kql9JJBBcCh1hm8ZXwG6InljEF-_H26GLmFZ0vdJAqj45y1tWTvE0s8cazXpA0PMlTYThi8C8oWHOgwEBs0Mj2hOVKBY__K8KNpur6_9iRSE7DdO4NFduY9zTlC1zYM2jd8vpKX3O6dVc0oydB27u5QHCaO3w1IdjCmZFSEQBHgd-nzIYLrlLBjd77yyiEEzwlANn5i2JXQp9FdR1hNRQw8TFvCIX_R9pL68wnX0="

# Channel details
SOURCE_CHANNEL = -1002118541881  # Source channel ID
DEST_CHANNEL = -1002696495424    # Destination channel ID

# Initialize the Telegram Client with session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Store forwarded file hashes to prevent duplicates
forwarded_files = set()

def get_file_hash(message):
    """Generate a hash for the file to detect duplicates."""
    if message.file:
        return hashlib.md5(str(message.file.id).encode()).hexdigest()
    return None

async def forward_all_messages():
    """ Forward all existing messages from the source channel without duplicates. """
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media:
            file_hash = get_file_hash(message)
            if file_hash and file_hash not in forwarded_files:
                try:
                    if message.file and message.file.ext.lower() in [".mp4", ".mkv"]:  # Only forward videos
                        await message.forward_to(DEST_CHANNEL)
                        forwarded_files.add(file_hash)
                        print(f"✅ Forwarded: {message.id}")
                        await asyncio.sleep(2.7)  # Prevent flood wait
                except Exception as e:
                    print(f"⚠️ Error forwarding {message.id}: {e}")
                    await asyncio.sleep(10)  # Extra delay on error

@client.on(events.NewMessage(chats=[SOURCE_CHANNEL]))
async def new_message_handler(event):
    """ Forward new incoming messages from the source channel without duplicates. """
    if event.message.media:
        file_hash = get_file_hash(event.message)
        if file_hash and file_hash not in forwarded_files:
            try:
                if event.message.file and event.message.file.ext.lower() in [".mp4", ".mkv"]:
                    await event.message.forward_to(DEST_CHANNEL)
                    forwarded_files.add(file_hash)
                    print(f"✅ Forwarded new message: {event.message.id}")
            except Exception as e:
                print(f"⚠️ Error forwarding new message: {e}")
                await asyncio.sleep(10)  # Extra delay on error

async def test_access():
    """ Test if the bot has access to the source channel. """
    try:
        entity = await client.get_entity(SOURCE_CHANNEL)
        print(f"✅ Bot has access to {entity.title} ({SOURCE_CHANNEL})")
    except Exception as e:
        print(f"❌ Error accessing source channel: {e}")

async def main():
    """ Main function to start the bot and check connection. """
    print("🚀 Starting userbot...")
    while True:
        try:
            await client.connect()
            
            if not await client.is_user_authorized():
                print("❌ Session is not authorized! Check SESSION_STRING.")
                return
            
            print("✅ Userbot started! Listening for new messages...")
            await test_access()
            await forward_all_messages()
            await client.run_until_disconnected()
        except Exception as e:
            print(f"⚠️ Connection lost! Reconnecting in 10 seconds... Error: {e}")
            await asyncio.sleep(10)

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
