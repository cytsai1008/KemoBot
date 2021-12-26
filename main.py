import os
import discord
import queue
import yt_dlp
import website
from unilog import log

intents = discord.Intents.all()
client = discord.Client(intents=intents)

class voice:
  def __init__(self, voice_ch, client, volume = 0.1):
    self.voice_ch = voice_ch
    self.client = client
    self.volume = volume

myvoice = voice(None, None)
music_list = queue.Queue()


def music_list_clear():
  with music_list.mutex:
    music_list.queue.clear()


def music_download(url: str) -> bool:
  log(f"Try downloading: {url}")
  #return True if noting went wrong
  try:
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
        os.rename(file, "music.mp3")
    log("The download was successful")
    return True
  except Exception as e:
    log(f"The download failed:\n{e}")
    return False


def playnext(error = None):
  if(not music_list.empty()):
    if(music_download(music_list.get())):
      song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("music.mp3"), myvoice.volume)
      myvoice.client.play(song, after=playnext)
  else:
    try:
      if(os.path.exists("music.mp3")):
        os.remove("music.mp3")
    except:
      pass


@client.event
async def on_ready():
  log(f"Signed in as: {client.user}")


@client.event
async def on_message(message):
  if(message.author == client.user):
    return #Prevent self-replying

  if(f"<@!{client.user.id}>" in message.content):
    await message.channel.send("omg i got mentioned (/ω＼)")

  command: str = ""
  value: str = ""
  has_voice_client: bool = (not myvoice.client is None and myvoice.client.is_connected())
  same_voice_channel: bool = (not message.author.voice is None and myvoice.voice_ch == message.author.voice.channel)

  if(message.content.startswith("?") and len(message.content) > 1):
    content: list = message.content[1:].split(" ", 1)
    command = content[0]
    if(len(content) > 1):
      value = content[1]
  else:
    return
  
  if(command == "summon"):
    if(has_voice_client and same_voice_channel):
      await message.channel.send("I'm already here!")
      return
    if(has_voice_client):
      if(not myvoice.client.is_playing()):
        await myvoice.client.disconnect()
      else:
        await message.channel.send("Sorry, but I'm playing music on another channel.")
        return      
    myvoice.voice_ch = message.author.voice.channel
    myvoice.client = await myvoice.voice_ch.connect()
  
  elif(command == "play"):
    if(value == ""):
      await message.channel.send("urlを提供するのを忘れちゃいました！")
      return
    if(message.author.voice is None):
      await message.channel.send("それを行うにはボイスチャンネルに入るのが必要です。")
      return
    if(has_voice_client and not same_voice_channel and myvoice.client.is_playing()):
      await message.channel.send("Sorry, but I'm playing music on another channel.")
      return
    if(has_voice_client and myvoice.client.is_playing()):
      music_list.put(value)
      await message.channel.send("キューに追加済み！")
      return
    if(not has_voice_client):
      myvoice.voice_ch = message.author.voice.channel
      myvoice.client = await myvoice.voice_ch.connect()
    elif(not myvoice.client.is_playing() and not same_voice_channel):
      await myvoice.client.disconnect()
      myvoice.voice_ch = message.author.voice.channel
      myvoice.client = await myvoice.voice_ch.connect()
    if(not music_download(value)):
      await message.channel.send("この曲のダウンロードに失敗しました。すみません。;w;")
      return
    song = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("music.mp3"), myvoice.volume)
    myvoice.client.play(song, after=playnext)

  elif(command == "pause" and myvoice.client.is_playing()):
    myvoice.client.pause()

  elif(command == "resume" and not myvoice.client.is_playing()):
    myvoice.client.resume()

  elif(command == "stop" and myvoice.client.is_playing()):
    music_list_clear()
    myvoice.client.stop()

  elif(command == "skip" and myvoice.client.is_playing()):
    myvoice.client.stop()

  elif(command == "leave" and not myvoice.client is None):
    music_list_clear()
    myvoice.client.stop()
    await myvoice.client.disconnect()

  elif(command == "game"):
    game = discord.Game(value)
    await client.change_presence(status=discord.Status.online, activity=game)
    
  elif(command == "help"):
    file = open("help.md")
    text = file.read()
    file.close()
    await message.channel.send(text)
    
  elif(command == "bug"):
    if(value == ""):
      await message.channel.send("Please try to describe the issue, like **?bug Cannot play the music**, and I'll fix them as soon as possible ;)")
      return
    await message.channel.send("Got it! Thank you so much for letting me know! I'll fix them as soon as possible 💖")
    await client.get_channel(924519224632815636).send(f"Bug report: '{value}' in '#{message.channel.name}'")


website.alive()
client.run(os.environ["TOKEN"])