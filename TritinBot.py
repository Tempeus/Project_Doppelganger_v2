import os
from discord.ext import commands
import discord
from dotenv import load_dotenv
import concurrent.futures
import asyncio
from openai import AsyncOpenAI
import random

# environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_KEY')

PERSONALITY = open("personality.txt").read()
# Message Queue Variables #
MAX_QUEUE_LENGTH = 20
MAX_WORKERS = 100 # Maximum number of threads you can process at a time 

message_queue = []
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []

# Define your intents
intents = discord.Intents.default()
intents.members = False  # Disable typing events, if needed
intents.presences = False  # Disable presence events, if needed
intents.message_content = True    # Enable message content updates (required for commands)

# Initialize the bot with the intents
bot = commands.Bot(command_prefix='!', intents=intents)

def event_with_probability(probability):
    return random.uniform(0, 1) <= probability

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_KEY,
)

async def generate_response(user_message):
    # Call ChatGPT API to get a response
    print("generating response to: ")
    print(user_message)
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": PERSONALITY + user_message,
            }
        ],
        model="gpt-3.5-turbo",
    )
    print("log: ", response)
    return response.choices[0].message.content

@bot.event
async def on_message(message):
    if message.channel.name == 'games-anime-memes':
        if bot.user.mentioned_in(message):
            # Get the user's message
            user_message = message.content.replace(f'<@!{bot.user.id}>', '').strip()
            response = await generate_response(user_message)

            # Send the response back to the Discord channel
            await message.channel.send(response)

        elif not message.author.bot and event_with_probability(0.05):
            user_message = message.content.strip()
            response = await generate_response(user_message)

            # Send the response back to the Discord channel
            await message.channel.send(response)

    await bot.process_commands(message)
bot.run(TOKEN)