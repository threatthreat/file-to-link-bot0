import asyncio
import random
import hashlib
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
import threading

# API Details
API_ID = 28866244  
API_HASH = "e6ade414044776910e7c63ff4643a7b0"
SESSION_STRING = "1BVtsOKYBu2NOfK00wpq9jyAdscYD8L0cjt27uMTLhyiiC1T5y4QXeoT7tmzJ8CweFxfQVCQCWjBAEDlTBZPjpUJ1aAZrt_IhaZx44ZPVdHyp19afL6EgMz9kql9JJBBcCh1hm8ZXwG6InljEF-_H26GLmFZ0vdJAqj45y1tWTvE0s8cazXpA0PMlTYThi8C8oWHOgwEBs0Mj2hOVKBY__K8KNpur6_9iRSE7DdO4NFduY9zTlC1zYM2jd8vpKX3O6dVc0oydB27u5QHCaO3w1IdjCmZFSEQBHgd-nzIYLrlLBjd77yyiEEzwlANn5i2JXQp9FdR1hNRQw8TFvCIX_R9pL68wnX0="

# Channel details
SOURCE_CHANNEL = -1002118541881  
DEST_CHANNEL = -1002696495424    

# Initialize Telegram Client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Track forwarded files to prevent duplicates
forwarded_files = set()
file_count = 0  
delay = random.randint(8, 15)  
restricted = False  

def get_file_hash(message):
    """Generate a hash for the file to detect duplicates."""
    if message.file:
        return hashlib.md5(str(message.file.id).encode()).hexdigest()
    return None

async def adjust_speed():
    """ Adjust speed dynamically based on Telegram's response. """
    global delay, restricted
    if restricted:
        delay = min(delay + 5, 40)  
        print(f"⚠️ Restricted! Increasing delay to {delay} sec...")
    else:
        delay = max(delay - 2, 8)  
        print(f"✅ Unrestricted! Decreasing delay to {delay} sec...")

async def forward_messages():
    """ Forward messages with auto-reconnect. """
    global file_count, delay, restricted
    while True:
        try:
            async for message in client.iter_messages(SOURCE_CHANNEL):
                if message.media:
                    file_hash = get_file_hash(message)
                    if file_hash and file_hash not in forwarded_files:
                        try:
                            if message.file and message.file.ext.lower() in [".mp4", ".mkv"]:
                                await message.forward_to(DEST_CHANNEL)
                                forwarded_files.add(file_hash)
                                file_count += 1
                                print(f"✅ Forwarded: {message.id} | Total: {file_count} | Delay: {delay} sec")

                                await adjust_speed()
                                await asyncio.sleep(delay)

                                if file_count % 1000 == 0:
                                    print("🔄 Processed 1000 files. Taking a 5-minute break...")
                                    await asyncio.sleep(300)

                                if file_count % 5000 == 0:
                                    print("🚀 5000 files forwarded. Taking a 30-minute break...")
                                    await asyncio.sleep(1800)

                        except Exception as e:
                            print(f"⚠️ Error forwarding {message.id}: {e}")
                            restricted = True  
                            await asyncio.sleep(20)

        except Exception as e:
            print(f"⚠️ Disconnected! Reconnecting in 10 sec... Error: {e}")
            await asyncio.sleep(10)

@client.on(events.NewMessage(chats=[SOURCE_CHANNEL]))
async def new_message_handler(event):
    """ Forward new messages with auto-reconnect. """
    global file_count, delay, restricted
    while True:
        try:
            if event.message.media:
                file_hash = get_file_hash(event.message)
                if file_hash and file_hash not in forwarded_files:
                    try:
                        if event.message.file and event.message.file.ext.lower() in [".mp4", ".mkv"]:
                            await event.message.forward_to(DEST_CHANNEL)
                            forwarded_files.add(file_hash)
                            file_count += 1
                            print(f"✅ Forwarded new message: {event.message.id} | Total: {file_count} | Delay: {delay} sec")

                            await adjust_speed()
                            await asyncio.sleep(delay)

                            if file_count % 1000 == 0:
                                print("🔄 Processed 1000 files. Taking a 5-minute break...")
                                await asyncio.sleep(300)

                            if file_count % 5000 == 0:
                                print("🚀 5000 files forwarded. Taking a 30-minute break...")
                                await asyncio.sleep(1800)

                    except Exception as e:
                        print(f"⚠️ Error forwarding new message: {e}")
                        restricted = True  
                        await asyncio.sleep(20)

        except Exception as e:
            print(f"⚠️ Disconnected! Reconnecting in 10 sec... Error: {e}")
            await asyncio.sleep(10)

async def check_connection():
    """ Check if bot is connected, if not, reconnect. """
    while True:
        if not await client.is_connected():
            print("⚠️ Bot disconnected! Reconnecting...")
            await client.connect()
        await asyncio.sleep(30)  

async def main():
    """ Start bot with auto-reconnect. """
    while True:
        try:
            print("🚀 Starting userbot...")
            await client.start()
            print("✅ Userbot started! Listening for new messages...")
            await asyncio.gather(forward_messages(), check_connection(), client.run_until_disconnected())
        except Exception as e:
            print(f"⚠️ Error: {e}. Restarting in 10 sec...")
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
