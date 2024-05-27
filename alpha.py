# Discord App Dependencies
import discord
from discord.ext import commands

# Media Downloader
from instabot import Bot
import tempfile
from instaloader import Instaloader, Profile
from instaloader.exceptions import InstaloaderException
from pytube import YouTube
from TikTokApi import TikTokApi
from moviepy.editor import VideoFileClip
from tiktokpy import TikTokPy
import tweepy  # Import the entire tweepy module
from tweepy import OAuthHandler, API  # Import specific classes from tweepy

# Google AI Studio Dependencies
import google.generativeai as genai

# System & File Dependencies
import os
import glob
from dotenv import load_dotenv

# Scrapping Dependencies
import requests
import urllib.parse
from urllib.parse import urlparse


# Image Processing Dependencies
from PIL import Image
import PIL.Image
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Get Discord and API tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)

# Retrieve Twitter API credentials
consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

# Set up tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


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
bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener for when the bot is ready


@bot.event
async def on_ready():
    guild_count = len(bot.guilds)
    print(f"SampleDiscordBot is in {guild_count} guilds.")
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

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
                img.save("local_image.jpg")
            except:
                await attachment.save("input." + os.path.splitext(attachment.filename)[1][1:])

    if message.content.startswith("GAMBARBOT"):

        model = genai.GenerativeModel(
            model_name="gemini-pro-vision",
            generation_config=generation_config,
            safety_settings=safety_settings,)
        imageAI = PIL.Image.open("local_image.jpg")

        bot_command = message.content[10:]
        response = model.generate_content([bot_command, imageAI], stream=True)
        response.resolve()
        await message.channel.send(response.text)

    if message.content.startswith("BOT"):

        model = genai.GenerativeModel(
            model_name="gemini-pro",
            generation_config=generation_config,
            safety_settings=safety_settings,)

        bot_command = message.content[4:]
        convo.send_message(bot_command)
        print(bot_command)
        await message.channel.send(convo.last.text)
    if message.content.startswith('!media'):
        # Process !media command
        video_url = message.content.split(' ')[1]
        await download_media(message, video_url)
    else:
        await bot.process_commands(message)


async def download_media(ctx, tweet_url):
    if 'x.com' in tweet_url:
        await download_twitter_media(ctx, tweet_url)
    else:
        await ctx.send('Please specify a valid Twitter link.')


async def download_twitter_media(ctx, tweet_url):
    tweet_id = tweet_url.split('/')[-1].split('?')[0]

    try:
        tweet = api.get_status(tweet_id, tweet_mode='extended')
        media = tweet.extended_entities['media'][0]
        media_url = media['media_url_https']

        # Download the media using requests
        response = requests.get(media_url, stream=True)

        # Create a download path
        download_path = f"./downloads/{tweet_id}/"
        os.makedirs(download_path, exist_ok=True)

        # Save the media file
        with open(f"{download_path}/media.{media_url.split('.')[-1]}", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        await ctx.send(f"Media downloaded successfully for tweet ID {tweet_id}.")
    except tweepy.TweepError as e:
        await ctx.send(f"Error: Unauthorized - {str(e)}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {str(e)}")




# Run the bot with the specified Discord token
bot.run(DISCORD_TOKEN)
