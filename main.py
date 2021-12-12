import os #for replit
import discord
import queue
import yt_dlp

intents = discord.Intents.all()
client = discord.Client(intents = intents)

class voice:
  def __init__(self, channel, client, volume = 0.1):
    self.channel = channel
    self.client = client
    self.volume = volume

myvoice = voice(None, None)
music_list = queue.Queue()


def music_download(url: str) -> str:
  url = url.split("&")[0]
  ydl_opts = {
      "format": "bestaudio/best",
      "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
      }],
    }
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")


def playnext(error = None):
  if(not music_list.empty()):
    song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"), myvoice.volume)
    myvoice.client.play(song, after=playnext)


@client.event
async def on_ready():
  print("Signed in as:", client.user)


@client.event
async def on_message(message):
  if(message.author == client.user):
    return #Prevent self-replying

  command: str = ""
  value: str = ""

  if(message.content.startswith("?") and len(message.content) > 1):
    content: list = message.content[1:].split(" ")
    command = content[0]
    if(len(content) > 1):
      value = content[1]
  else:
    return

  if(command == "play"):
    if(value == ""):
      await message.channel.send("Empty url.")
      return

    if(not myvoice.client is None and myvoice.client.is_playing()):
      music_list.put(value)
      await message.channel.send("Music queued!")
      return

    music_download(value)
    
    myvoice.channel = message.author.voice.channel
    if(myvoice.client is None or not myvoice.client.is_connected()):
      myvoice.client = await myvoice.channel.connect()

    song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("song.mp3"), myvoice.volume)
    myvoice.client.play(song, after=playnext)

  elif(command == "pause" and myvoice.client.is_playing()):
    myvoice.client.pause()

  elif(command == "resume" and not myvoice.client.is_playing()):
    myvoice.client.resume()

  elif(command == "stop" and myvoice.client.is_playing()):
    myvoice.client.stop()

  elif(command == "skip" and myvoice.client.is_playing()):
    myvoice.client.stop()
    playnext()

  elif(command == "leave" and myvoice.client.is_connected()):
    await myvoice.client.disconnect()

  elif(command == "help"):
    file = open("help.md")
    text = file.read()
    file.close()
    await message.channel.send(text)
    

client.run(os.environ["TOKEN"])