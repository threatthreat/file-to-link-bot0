from telethon import TelegramClient, events
import asyncio
import os
from flask import Flask

# Load API details from environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "teleb"

# Source & Destination Channel IDs
SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL"))
DEST_CHANNEL = int(os.getenv("DEST_CHANNEL"))

# Initialize Telethon client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def forward_all_messages():
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media:
            try:
                await message.forward_to(DEST_CHANNEL)
                print(f"Forwarded: {message.id}")
                await asyncio.sleep(3)  # Prevent flood wait
            except Exception as e:
                print(f"Error forwarding {message.id}: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    if event.message.media:
        try:
            await event.message.forward_to(DEST_CHANNEL)
            print(f"Forwarded new message: {event.message.id}")
        except Exception as e:
            print(f"Error forwarding new message: {e}")

async def start_bot():
    print("Starting userbot...")
    await client.start()
    print("Userbot started successfully!")
    await forward_all_messages()
    print("Listening for new messages...")
    await client.run_until_disconnected()

# Dummy Web Server for Health Check
app = Flask(__name__)

@app.route('/')
def home():
    return "Userbot is running!", 200

# Run Flask & Telethon together
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())  # Start Telethon bot
    app.run(host="0.0.0.0", port=8000)  # Start Flask web server
