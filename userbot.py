from telethon import TelegramClient, events
import asyncio

# Your Telegram API details
API_ID = "28866244"
API_HASH = "e6ade414044776910e7c63ff4643a7b0"

# Your session name (file will be created)
SESSION_NAME = "teleb"

# Channel details
SOURCE_CHANNEL = -1002118541881  # Replace with the source channel ID
DEST_CHANNEL = -1002613474973   # Replace with your private channel ID

# Initialize the client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def forward_all_messages():
    async for message in client.iter_messages(SOURCE_CHANNEL):
        if message.media:
            try:
                await message.forward_to(DEST_CHANNEL)
                print(f"Forwarded: {message.id}")
                await asyncio.sleep(2)  # Prevents flood wait
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

async def main():
    print("Starting userbot...")
    await forward_all_messages()  # Forward old messages
    print("Listening for new messages...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
