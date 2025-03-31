from telethon import TelegramClient, events
import asyncio
import os
from telethon.sessions import StringSession
from flask import Flask
import threading

# API Details
API_ID = 28866244  # Ensure it's an integer
API_HASH = "e6ade414044776910e7c63ff4643a7b0"

# Use your session string directly
SESSION_STRING = "1BVtsOHcBu2KmILIwVTdhfIyrCxx90tjXlMkXHDsTGroLTPVYJCw0iHMvD8meJG7e2mPXD8I2SNL7PvgJjvzU7P31ku1ERBWuQorVJTDm6JzHipPGZt6WUdqS9bFicN2nkZrcx9zchGDiEIEzjDnEjV_y4EOe2QT3_gGAfjUxsZsOaHpV_eefyYX8IgT4LL5djWp_HqgFzUM3OEe4iVCvKMTOaiVr6mXb4hPLNBe-OZsXXJeNMIW5aFfFOo4sQRLR1ni9i0Hshh5nGNVjoi9SMWEEsHCWzWlnHciLSDfhGyNxvmaXR8sBTFwZAoNhwBHYGgRTXIYkSUo9bX5tA7hkbqekKX9LYpE="

# Channel details
SOURCE_CHANNEL = -1002118541881  # Source channel ID
DEST_CHANNEL = -1002696495424    # Destination channel ID

# Initialize the Telegram Client with session string
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Store forwarded message IDs to prevent duplicates
forwarded_messages = set()

async def forward_all_messages():
    """ Forward all existing messages from the source channel without duplicates. """
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media and message.id not in forwarded_messages:
            try:
                if message.file.ext.lower() in [".mp4", ".mkv"]:  # Only forward videos (MP4, MKV)
                    await message.forward_to(DEST_CHANNEL)
                    forwarded_messages.add(message.id)
                    print(f"✅ Forwarded: {message.id}")
                    await asyncio.sleep(2.7)  # Prevent flood wait
            except Exception as e:
                print(f"⚠️ Error forwarding {message.id}: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    """ Forward new incoming messages from the source channel without duplicates. """
    if event.message.media and event.message.id not in forwarded_messages:
        try:
            if event.message.file.ext.lower() in [".mp4", ".mkv"]:  # Only forward videos (MP4, MKV)
                await event.message.forward_to(DEST_CHANNEL)
                forwarded_messages.add(event.message.id)
                print(f"✅ Forwarded new message: {event.message.id}")
        except Exception as e:
            print(f"⚠️ Error forwarding new message: {e}")

async def main():
    """ Main function to start the bot. """
    print("🚀 Starting userbot...")
    await client.start()  # No OTP required since session string is used
    print("✅ Userbot started! Listening for new messages...")
    await forward_all_messages()  # Forward old messages
    await client.run_until_disconnected()

# Flask App for UptimeRobot
app = Flask(__name__)

@app.route("/")
def home():
    return "Userbot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Run Flask in a
