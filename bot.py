import discord
import os
from pdf2image import convert_from_bytes
from dotenv import load_dotenv
import requests
from tempfile import TemporaryDirectory

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


async def send_pdf_as_images(message, url):
    pdf_bytes = requests.get(url, stream=True)
    more_than_ten_pages = False
    with TemporaryDirectory() as path:
        images = convert_from_bytes(pdf_bytes.raw.read(
        ), paths_only=True, output_folder=path, grayscale=True, last_page=11, fmt='.png', thread_count=4)

        if len(images) > 10:
            more_than_ten_pages = True
            # NOTE: Don't return: we want to send the images anyway
            images = images[:10]
        files = [discord.File(fp=filename, filename=f"page_{idx + 1}.png")
                 for idx, filename in enumerate(images)]
        await message.channel.send(files=files)

    if more_than_ten_pages:
        warning_message = "**WARN**: Your PDF was more than 10 pages long: only sending the first 10 pages"
        await message.channel.send(warning_message)


@client.event
async def on_message(message):
    if message.author.bot:
        return
    for attachment in message.attachments:
        if not attachment.filename.endswith('.pdf'):
            continue
        await send_pdf_as_images(message, attachment.url)


print(TOKEN)
client.run(TOKEN)
