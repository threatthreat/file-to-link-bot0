from telethon import TelegramClient, events
import asyncio
import os

# Load API details from environment variables (recommended for Railway)
API_ID = int(os.getenv("API_ID", 28866244))  # Ensure it's an integer
API_HASH = os.getenv("API_HASH", "e6ade414044776910e7c63ff4643a7b0")
SESSION_NAME = "teleb"  # Ensure this file is uploaded to Railway
SESSION_FILE = f"{SESSION_NAME}.session"  # Actual session file

# Channel details
SOURCE_CHANNEL = -1002118541881  # Source channel ID
DEST_CHANNEL = -1002613474973   # Destination channel ID

# Ensure session file exists
if not os.path.exists(SESSION_FILE):
    print(f"❌ Session file '{SESSION_FILE}' not found! Make sure it's in your Railway repo.")
    exit(1)

# Initialize the Telegram Client with session file
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

async def forward_all_messages():
    """ Forward all existing messages from the source channel. """
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media:
            try:
                await message.forward_to(DEST_CHANNEL)
                print(f"✅ Forwarded: {message.id}")
                await asyncio.sleep(3)  # Prevent flood wait
            except Exception as e:
                print(f"⚠️ Error forwarding {message.id}: {e}")

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
    """ Main function to start the bot. """
    print("🚀 Starting userbot...")
    await client.connect()  # Connect without asking for input
    if not await client.is_user_authorized():
        print("❌ Session is invalid. Please re-login locally and re-upload the session file.")
        exit(1)

    print("✅ Userbot started! Listening for new messages...")
    await forward_all_messages()  # Forward old messages
    await client.run_until_disconnected()

if __name__ == "__main__":
    client.loop.run_until_complete(main())
