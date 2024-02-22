# Discord App Dependencies
import discord
from discord.ext import commands
from typing import Optional
from discord import app_commands

# System & File Dependencies
import os
import glob
from dotenv import load_dotenv
from urllib.parse import quote

# Google AI Studio Dependencies
import google.generativeai as genai


# joke api
from jokeapi import Jokes

# Image Processing Dependencies
from PIL import Image
import PIL.Image
from io import BytesIO

# Scrapping Dependencies
import requests
import urllib.parse
from urllib.parse import urlparse
import traceback

# Remove Background Dependencies
from rembg import remove

# PDF converter Dependencies
from spire.doc import *
from spire.doc.common import *

# DuckDuckGo Dependencies
from duckduckgo_search import DDGS

# Import Random
from datetime import datetime
import random

# import from googlesearch import search
from googlesearch import search
# import json
import json

# import function
from hentai_func import Hentai, NekosFunTags, NsfwApis


# Load environment variables from .env file
load_dotenv()
# commands = commands.Bot(command_prefix='')

# Get Discord and API tokens from environment variables
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")


# Set up the generative model
generation_config = {
    "temperature": 0.5,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 400,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,)

convo = model.start_chat(history=[])

# Create Discord client with intents
intents = discord.Intents.all()
bot = discord.Client(intents=intents)
game = discord.Game("Naughty")

# Event listener for when the bot is ready


@bot.event
async def on_ready():
    print('Bot is ready!')
    guild_count = len(bot.guilds)
    print(f"SampleDiscordBot is in {guild_count} guilds.")
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
    print('Bot is ready!')
    await bot.change_presence(status=discord.Status.idle, activity=game)
# Event listener for new messages


@bot.event
async def on_message(message):
    if message.attachments:
        model = genai.GenerativeModel(
            model_name="gemini-pro-vision",
            generation_config=generation_config,
            safety_settings=safety_settings,)
        for attachment in message.attachments:
            try:
                image_url = attachment.url
                print(image_url)
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                # Check if the image format is not JPEG, then convert to JPEG
                if img.format != "JPEG":
                    img.save("local_image.jpg", format="JPEG")
                else:
                    img.save("local_image.jpg")
            except Exception as e:
                print(f"Error: {e}")
                # If there's an error, save the image with its original extension
                await attachment.save(f"local_image.{os.path.splitext(attachment.filename)[1][1:]}")

    if message.content.startswith("GAMBARTOD"):
        model = genai.GenerativeModel(
            model_name="gemini-pro-vision",
            generation_config=generation_config,
            safety_settings=safety_settings,)
        image_path_jpg = "local_image.jpg"
        image_path_png = "local_image.png"
        try:
            imageAI = PIL.Image.open(image_path_jpg)
        except FileNotFoundError:
            try:
                imageAI = PIL.Image.open(image_path_png)
            except FileNotFoundError:
                await message.channel.send("Image not found.")
                return
        bot_command = message.content[10:]
        response = model.generate_content([bot_command, imageAI], stream=True)
        response.resolve()
        await message.channel.send(response.text)

    if message.content.startswith("BGREM"):
        input_path_jpg = 'local_image.jpg'
        input_path_png = 'local_image.png'
        output_path = 'output.png'
        try:
            with open(input_path_jpg, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input_data = i.read()
                    output_data = remove(input_data)
                    o.write(output_data)
            with open(output_path, 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)
        except FileNotFoundError:
            try:
                with open(input_path_png, 'rb') as i:
                    with open(output_path, 'wb') as o:
                        input_data = i.read()
                        output_data = remove(input_data)
                        o.write(output_data)

                with open(output_path, 'rb') as f:
                    picture = discord.File(f)
                    await message.channel.send(file=picture)
            except FileNotFoundError:
                await message.channel.send("Image not found.")

    if message.content.startswith("TOD"):
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings,)

        bot_command = message.content[4:]
        convo.send_message(bot_command)
        print(bot_command)
        await message.channel.send(convo.last.text)

    # Send a DM to a specific user with a custom message
    if message.content.startswith("DM"):
        # Split the message into parts: "DM username custom_message"
        parts = message.content.split(" ", 2)

        # Check if there are enough parts
        if len(parts) == 3:
            user_name = parts[1]
            custom_message = parts[2]

            # Find the target user by name
            target_user = discord.utils.get(
                message.guild.members, name=user_name)

            # Check if the target user exists
            if target_user:
                # Send a direct message with the custom message
                await target_user.send(f"📬 From {message.author.name} say: {custom_message}")
                await message.channel.send(f"✉️ Custom message sent to {target_user.name}.")
            else:
                await message.channel.send(f"❌ User '{user_name}' not found.")
        else:
            await message.channel.send("⚠️ Invalid syntax. Use 'DM username custom_message'")

    # Command to get a joke
    if message.content.startswith("!joke"):
        j = await Jokes()
        blacklist = ["racist"]
        if not message.channel.is_nsfw():
            blacklist.append("nsfw")
        joke_data = await j.get_joke(blacklist=blacklist)
        msg = ""
        if joke_data["type"] == "single":
            msg = joke_data["joke"]
        else:
            msg = joke_data["setup"]
            msg += f"||{joke_data['delivery']}||"
        await message.channel.send(msg)

    if message.content.startswith("CARIGAMBAR"):
        bot_command = message.content[11:]
        imageURL = {}

        with DDGS() as ddgs:
            keywords = bot_command
            ddgs_images_gen = ddgs.images(
                keywords,
                region="wt-wt",
                safesearch="off",
                size=None,
                # color="Monochrome",
                type_image=None,
                layout=None,
                license_image=None,
                max_results=2,
            )
            for r in ddgs_images_gen:
                imageURL = r
                image_url = imageURL.get('image', None)

                response = requests.get(image_url)
                if response.status_code == 200:
                    parsed_url = urlparse(image_url)
                    file_extension = os.path.splitext(parsed_url.path)[1]
                    filename = f"downloaded_image{file_extension}"
                    # Save the image to the local file
                    with open(filename, 'wb') as thefile:
                        thefile.write(response.content)
                        print(f"Image downloaded and saved as: {filename}")
                    with open(filename, 'rb') as f:
                        picture = discord.File(f)
                        await message.channel.send(file=picture)
                else:
                    print(
                        f"Failed to download image. Status code: {response.status_code}")
    if message.content.startswith("!userinfo"):
        bot_command = message.content[10:]
        # Panggil fungsi user_info dan kirimkan message serta bot_command sebagai parameter
        await user_info(message, bot_command)
    if message.content.startswith("!google"):
        # Ekstrak query dari pesan
        query = message.content[8:]
        # Lakukan pencarian Google
        search_results = google_search(query)
        # Kirim hasil pencarian ke channel
        await message.channel.send(f"**Google Search Results for '{query}':**\n" + "\n".join(search_results))

    if message.content.startswith('cari'):
        try:
            if len(message.attachments) == 1:
                gambar = message.attachments[0].url
                encoded_url = quote(gambar)
                await message.reply('Mencari anime...')
                apiurl = 'https://api.trace.moe/search?anilistInfo&url=' + encoded_url
                r = requests.get(apiurl)
                detik = int(r.json()['result'][0]['from'])
                m, s = divmod(detik, 60)
                h, m = divmod(m, 60)
                # with embed
                judulnative = str(r.json()['result']
                                  [0]['anilist']['title']['native'])
                judulromaji = str(r.json()['result']
                                  [0]['anilist']['title']['romaji'])
                judulenglish = str(
                    r.json()['result'][0]['anilist']['title']['english'])
                eps = str(r.json()['result'][0]['episode'])
                menit = f'{h:d}:{m:02d}:{s:02d}'
                similiarity = '%.2f%%' % (
                    float(r.json()['result'][0]['similarity']) * 100) + ' similarity'
                embed = discord.Embed(color=discord.Color.dark_purple())
                embed.set_image(url=gambar)
                embed.add_field(name='Judul', value='Native:' + judulnative + '\n' +
                                'Romaji: ' + judulromaji + '\n' + 'English: ' + judulenglish, inline=False)
                embed.add_field(name='Episode', value=eps)
                embed.add_field(name='Pada menit ke', value=menit)
                embed.add_field(name='Similarity',
                                value=similiarity, inline=False)
                await message.reply(embed=embed)
                # this will get the video from the trace.moe API
                video = r.json()['result'][0]['video']
                reqvideo = requests.get(video)
                videoname = r.json()['result'][0]['filename'] + '.mp4'
                with open(videoname, 'wb') as f:
                    f.write(reqvideo.content)
                    f.close()
                # and then send the video
                await message.reply(file=discord.File(videoname))
                os.remove(videoname)
                if r.status_code == 200:
                    print(r.text)
                else:
                    print(
                        f"Failed to fetch image. Status code: {r.status_code}")
            elif len(message.attachments) > 1:
                await message.reply('Hanya boleh 1 gambar')
            else:
                await message.reply('Kirim gambar dulu!')
        except Exception as e:
            traceback.print_exc()
            await message.reply(f'Error: {e}')

    if message.content.startswith('rule34'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Rule34 content...")
            ret = await Hentai().get_nsfw_image(NsfwApis.Rule34Api)
            source = ret["source"]
            owner = ret["owner"]
            score = ret["score"]
            image = ret["file_url"]
            if image.endswith(".mp4"):
                await message.channel.send(image)
            else:
                embed = discord.Embed(title="Created by {}".format(owner))
                embed.color = discord.Color.random()
                if source != "":
                    embed.add_field(
                        name="Source", value="[Click here]({})".format(source), inline=True
                    )
                embed.add_field(name="Score", value=score, inline=True)
                embed.set_image(url=image)
                embed.set_footer(text="Fetched from Rule34")
                await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Rule34 content: {e}")

    if message.content.startswith('gelbooru'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Gelbooru content...")
            ret = await Hentai().get_nsfw_image(NsfwApis.GelbooruApi)
            source = ret["source"]
            owner = ret["owner"]
            score = ret["score"]
            image = ret["file_url"]
            created_at = ret["created_at"]
            if image.endswith(".mp4"):
                await message.channel.send(image)
            else:
                embed = discord.Embed(title="Created by {}".format(owner))
                embed.color = discord.Color.random()
                if source != "":
                    embed.add_field(
                        name="Source", value="[Click here]({})".format(source), inline=True
                    )
                embed.add_field(name="Score", value=score, inline=True)
                embed.set_image(url=image)
                embed.set_footer(
                    text="Fetched from Gelbooru\nCreated at {}".format(created_at))
                await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Gelbooru content: {e}")

    if message.content.startswith('yandere'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Yandere content...")
            ret = await Hentai().get_nsfw_image(NsfwApis.YandereApi)
            created_at = datetime.fromtimestamp(int(ret["created_at"]))
            file = ret["file_url"]
            author = ret["author"]
            source = ret["source"]
            score = ret["score"]
            embed = discord.Embed(title="Created by {}".format(author))
            embed.color = discord.Color.random()
            if source != "":
                embed.add_field(
                    name="Source", value="[Click here]({})".format(source), inline=True
                )
            embed.add_field(name="Score", value=score, inline=True)
            embed.set_image(url=file)
            embed.set_footer(
                text="Fetched from Yande.re\nCreated at {}".format(created_at))
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Yandere content: {e}")

    if message.content.startswith('konachan'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Konachan content...")
            ret = await Hentai().get_nsfw_image(NsfwApis.KonachanApi)
            created_at = datetime.fromtimestamp(int(ret["created_at"]))
            file = ret["file_url"]
            author = ret["author"]
            source = ret["source"]
            score = ret["score"]
            embed = discord.Embed(title="Created by {}".format(author))
            embed.color = discord.Color.random()
            if source != "":
                embed.add_field(
                    name="Source", value="[Click here]({})".format(source), inline=True
                )
            embed.add_field(name="Score", value=score, inline=True)
            embed.set_image(url=file)
            embed.set_footer(
                text="Fetched from Konachan\nCreated at {}".format(created_at))
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Konachan content: {e}")

    if message.content.startswith('danbooru'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Danbooru content...")
            ret = await Hentai().get_nsfw_image(NsfwApis.DanbooruApi)
            created_at = ret["created_at"]
            file = ret["file_url"]
            author = ret["tag_string_artist"]
            source = ret["source"]
            score = ret["score"]
            embed = discord.Embed(title="Created by {}".format(author))
            embed.color = discord.Color.random()
            if source != "":
                embed.add_field(
                    name="Source", value="[Click here]({})".format(source), inline=True
                )
            embed.add_field(name="Score", value=score, inline=True)
            embed.set_image(url=file)
            embed.set_footer(
                text="Fetched from Danbooru\nCreated at {}".format(created_at))
            await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Danbooru content: {e}")

    if message.content.startswith('nekosfun'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching NekosLife content...")
            tag = random.choice(list(NekosFunTags))
            image = Hentai.nekofun(tag.value)
            if image == False:
                await message.channel.send("An error has occurred!")
            else:
                embed = discord.Embed()
                embed.color = discord.Color.random()
                embed.set_image(url=image)
                embed.set_footer(text="Fetched from Nekos.Fun")
                await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching NekosLife content: {e}")

    if message.content.startswith('boobchi'):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        try:
            # Provide some feedback to the user
            await message.channel.send("Fetching Hitori Gotoh content...")
            image, source = Hentai.boobchi()
            if image == False:
                await message.channel.send("An error has occurred!")
            else:
                embed = discord.Embed()
                embed.color = discord.Color.random()
                embed.description = f"[Source]({source})"
                embed.set_image(url=image)
                embed.set_footer(text="Fetched from Bocchi-API")
                await message.channel.send(embed=embed)
        except Exception as e:
            await message.channel.send(f"Error fetching Hitori Gotoh content: {e}")
    if message.content.startswith("!hent"):
        if not message.channel.is_nsfw():
            await message.channel.send("This command can only be used in NSFW channels.")
            return
        nhentai = randomhen2()
        await message.channel.send(nhentai)
    if message.content.startswith("help"):
        await message.reply(help_message)
        return


# Fungsi user_info harus didefinisikan di luar event listener
async def user_info(message, user_mention):
    # Ambil objek Member dari pengguna yang disebutkan
    if message.mentions:
        member = message.mentions[0]
    else:
        member = message.author

    # Ambil waktu bergabung
    join_date = member.joined_at.strftime('%Y-%m-%d %H:%M:%S')

    # Tambahkan logika level dan poin sesuai kebutuhan
    level = random.randint(1, 10)  # Ganti dengan logika level sesuai kebutuhan
    # Ganti dengan logika poin sesuai kebutuhan
    points = random.randint(100, 1000)

    # Status Discord pengguna
    status = str(member.status).title()

    # Menampilkan avatar pengguna
    avatar_url = member.avatar_url_as(size=256)

    # Menampilkan aktivitas pengguna
    activities = ', '.join(
        [f'{act.name} ({act.type})' for act in member.activities])

    # Menampilkan detail server boost
    if member.premium_since:
        boost_date = member.premium_since.strftime('%Y-%m-%d %H:%M:%S')
        boost_info = f'{member.mention} adalah Server Booster sejak: {boost_date}'
    else:
        boost_info = f'{member.mention} bukan Server Booster.'

    # Menampilkan tag Discord
    discriminator = member.discriminator

    # Menampilkan jumlah pesan yang pernah dikirim oleh pengguna
    message_count = len(await message.channel.history(limit=None).flatten())

    # Saran acak untuk personalisasi pengalaman pengguna
    suggestions = [
        "Cobalah bergabung dengan salah satu voice channel untuk berbincang dengan anggota server!",
        "Jangan ragu untuk bertanya jika Anda memiliki pertanyaan atau membutuhkan bantuan.",
        "Selamat bersenang-senang di server ini!",
    ]
    random_suggestion = random.choice(suggestions)

    # Gabungkan semua informasi menjadi satu pesan
    user_info_message = (
        f'{boost_info}\n'
        f'Tag Discord: #{discriminator}\n'
        f'Jumlah Pesan yang Dikirim: {message_count}\n'
        f'Saran: {random_suggestion}\n\n'
        f'Waktu Bergabung: {join_date}\n'
        f'Level: {level}\n'
        f'Jumlah Poin: {points}\n'
        f'Status: {status}\n'
        f'Avatar: {avatar_url}\n'
        f'Aktivitas: {activities}'
    )
    # Kirim info pengguna sebagai satu pesan
    await message.channel.send(user_info_message)


# Fungsi untuk melakukan pencarian Google
def google_search(query, num_results=5):
    results = list(search(query, num_results=num_results))
    return results

def randomhen2():
    num = random.randint(1, 300000)
    hentai_pick = "https://nhentai.net/g/{}/".format(num)
    return (hentai_pick)


def delay_print(s):
    for c in s:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.05)


help_message = \
    """```
📣THE COMAND IN TEXT CHANEL
=> TOD
Chat percakapan dengan bot biasa 

=>GAMBARTOD
Chat percakapan bisa dengan tambahan gambar

=>BGREM
Menghapus Background gambar yang dikirim

=>DM
Bot Dapat meng DM orang dengan id user yang berada di server yang sama

=> !joke
Dapat melakukan joke dalam bahasa inggris

=>CARIGAMBAR
Mencari gambar dengan menggunakan serch enggine duckduck go

=>!userinfo
Mencari user info dengan men tag orang yang ingin di cari tahu

=>!google
Mencari sesuatu dengan search enggine google 


=>cari
Mencari suatu anime dengan kata cari + gambar



📣ONLY CAN ACCES THE COMAND IN NSFW TEXT CHANEL
=> rule34 
Get image/video from Rule34 (EXTREME CONTENT AHEAD!!!).

=> gelbooru 
Get image/video from Gelbooru

=>yandere 
Get image from Yande.re

=>konachan 
Get image from Konachan

=>danbooru 
Get image/video from Danbooru

=>nekosfun 
Get images/gifs from NekosLife

=>boobchi
Get a random ecchi image of Hitori Gotoh

=> !hent
Generate Random Nhentai Code

```"""


TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
