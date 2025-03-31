from telethon import TelegramClient, events
from telethon.sessions import StringSession
import asyncio
import os

# Your API details
API_ID = int(os.getenv("API_ID", 28866244))
API_HASH = os.getenv("API_HASH", "e6ade414044776910e7c63ff4643a7b0")

# Channel details
SOURCE_CHANNEL = -1002118541881  
DEST_CHANNEL = -1002696495424  

# Store session as a string in the same file
SESSION_STRING = os.getenv("SESSION_STRING", "1BVtsOHcBu2KmILIwVTdhfIyrCxx90tjXlMkXHDsTGroLTPVYJCw0iHMvD8meJG7e2mPXD8I2SNL7PvgJjvzU7P31ku1ERBWuQorVJTDm6JzHipPGZt6WUdqS9bFicN2nkZrcx9zchGDiEIEzjDnEjV_y4EOe2QT3_gGAfjUxsZsOaHpV_eefyYX8IgT4LL5djWp_HqgFzUM3OEe4iVCvKMTOaiVr6mXb4hPLNBe-OZsXXJeNMIW5aFfFOo4sQRLR1ni9i0Hshh5nGNVjoi9SMWEEsHCWzWlnHciLSDfhGyNxvmaXR8sBTFwZAoNhwBHYGgRTXIYkSUo9bX5tA7hkbqekKX9LYpE=")

# If session exists, use it; otherwise, create a new one
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

# Set to store forwarded message IDs (prevents duplicates)
forwarded_files = set()

# Allowed file types (MP4, MKV)
ALLOWED_TYPES = ["video/mp4", "video/x-matroska", "application/octet-stream"]

async def forward_all_messages():
    """ Forward all existing messages from the source channel. """
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media and message.id not in forwarded_files:
            if message.document and message.document.mime_type in ALLOWED_TYPES:
                try:
                    await message.forward_to(DEST_CHANNEL)
                    forwarded_files.add(message.id)  # Mark as forwarded
                    print(f"✅ Forwarded: {message.id}")
                    await asyncio.sleep(1.5)  # Prevent flood wait
                except Exception as e:
                    print(f"⚠️ Error forwarding {message.id}: {e}")

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def new_message_handler(event):
    """ Forward new incoming messages from the source channel. """
    if event.message.media and event.message.id not in forwarded_files:
        if event.message.document and event.message.document.mime_type in ALLOWED_TYPES:
            try:
                await event.message.forward_to(DEST_CHANNEL)
                forwarded_files.add(event.message.id)  # Mark as forwarded
                print(f"✅ Forwarded new message: {event.message.id}")
            except Exception as e:
                print(f"⚠️ Error forwarding new message: {e}")

async def main():
    """ Main function to start the bot. """
    global SESSION_STRING

    if not SESSION_STRING:
        print("🔑 First-time login: Enter your phone number and OTP.")
        await client.start()
        SESSION_STRING = client.session.save()  # Save session in the same file
        print(f"✅ Session saved. Use this string for future logins:\n{SESSION_STRING}")

    print("🚀 Userbot started! Listening for new messages...")
    await forward_all_messages()
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
