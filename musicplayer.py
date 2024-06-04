import discord
import asyncio
import os
import difflib
#import spotipy
import pathlib
from pytube import YouTube, exceptions as YTExceptions

intents = discord.Intents.default()
intents.message_content = True
Client = discord.Client(intents=intents)
Downloads = r'D:/User/Desktop/downloaded'

ErrorMessages = {'unavailable': r"Couldn't find youtube video!"}
Prefix = '+'
VoiceClients = dict()
GuildSongInfos = dict()
DefaultDict = {'VoiceClient': discord.VoiceClient, 'Loop': False, 'CurrentSong': str, 'MusicQueue': list(), 'Pause': False}

@Client.event
async def on_ready():
    print('bot is on')

def ChangeDictionary(Key, Value, GuildID):  
    VoiceClients[GuildID][Key] = Value
    print(VoiceClients)

def GetDictionary(Key, GuildID):
    return VoiceClients[GuildID][Key]

async def Play(Music, voice_client: discord.VoiceClient, vchannel: discord.VoiceChannel, msg: discord.Message):
    if not vchannel:
        await msg.reply("Join a voice channel to play songs!")
        return
    if not voice_client or not voice_client.is_connected():
        PlaySong = await vchannel.connect()
        VoiceClients[msg.guild.id] = DefaultDict
        ChangeDictionary('VoiceClient', PlaySong, msg.guild.id)
    VClient = GetDictionary('VoiceClient', msg.guild.id)
    if vchannel and VClient.channel != vchannel and not VClient.is_playing():
        PlaySong = await vchannel.connect()
        ChangeDictionary('VoiceClient', PlaySong, msg.guild.id)
    PlaySong = VoiceClients[msg.guild.id]['VoiceClient']
    if PlaySong.is_playing():
        OldMusicQueue = GetDictionary('MusicQueue', msg.guild.id)
        OldMusicQueue.insert(len(OldMusicQueue), Music)
        ChangeDictionary('MusicQueue', OldMusicQueue, msg.guild.id)
        await msg.reply(f'Added {os.path.basename(Music).replace(".mp4", "")} to queue (Number: {len(OldMusicQueue)})')
        return
    await msg.reply(f'Playing audio: {os.path.basename(Music)}')
    await Client.change_presence(activity=discord.Game(name=os.path.basename(Music).replace('.mp4', '')))
    PlaySong.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=Music))
    while PlaySong.is_playing():
        await asyncio.sleep(.3)
    if GetDictionary('Loop', msg.guild.id) == True:
        await Play(Music, PlaySong, vchannel, msg) 
    MusicQueue = GetDictionary('MusicQueue', msg.guild.id)
    if len(MusicQueue) > 0:
        CurrentMusic = MusicQueue[0]
        MusicQueue.remove(CurrentMusic)
        ChangeDictionary('MusicQueue', MusicQueue, msg.guild.id) 
        await Play(CurrentMusic, PlaySong, vchannel, msg)

os.chdir(Downloads)

async def DownloadVideo(link: str, Message: discord.Message):
    if link.lower().find('https://') != -1:
        try:
            await Message.reply('Downloading video, please wait!')
            VideoPath = YouTube(link).streams.filter(file_extension='mp4').first().download(output_path=Downloads)
            return VideoPath
        except YTExceptions.VideoUnavailable:
            return None

def Similarity(Name: str, Similars: list):
    return difflib.get_close_matches(Name, Similars, cutoff=0.1)

def FindVideoLinkDownloaded(Link: str):
    if Link.lower().find('https://') != -1:
        try:
            return YouTube(Link).streams.first().title
        except:
           print('e')
           return
    return
        
async def FindVideoDownloaded(Name: str, Message: discord.Message):
    Matches = list()
    for file in os.scandir():
        if file.is_file() and file.name.lower().find(Name) != -1:
            Matches.insert(len(Matches), pathlib.Path(file.path).stem)
    if len(Matches) > 0:
        MostSimilar = Similarity(Name, Matches)
        print(MostSimilar)
        if len(MostSimilar) > 0:
            return f'{Downloads}//{MostSimilar[0]}.mp4'
    VideoTitle = FindVideoLinkDownloaded(Name)
    if VideoTitle:
        print(VideoTitle.encode('utf-8'))
    if VideoTitle and f'{VideoTitle}.mp4' in os.listdir(): return f'{Downloads}//{VideoTitle}.mp4'
    return await DownloadVideo(Name, Message)

async def Skip(GuildID: int):
    Queue = GetDictionary('MusicQueue', GuildID)
    CurrentPlaying = GetDictionary("CurrentSong", GuildID)
    if CurrentPlaying in Queue:
        ChangeDictionary('MusicQueue', Queue.remove(CurrentPlaying))
    

@Client.event
async def on_message(Message: discord.Message):
    Command = Message.content.lower().split(' ')[0]
    if Message.author == Client.user: return
    Author = Message.author
    if Command.find(Prefix + 'play') != -1:
        Split = Message.content.split()
        Music = ' '.join(Split[1:len(Split)]) 
        if getattr(Author, 'voice'):
            Channel = Author.voice.channel
        else:
            Channel = None
        voice_client = Message.guild.voice_client
        audioPath = await FindVideoDownloaded(Music, Message)
        if audioPath != None:
            await Play(audioPath, voice_client, Channel, Message)
        else:
            await Message.reply("Couldn't find song, please specify the song name or provide youtube song link!")
    elif Command.find(Prefix + 'loop') != -1:
        ID = Message.guild.id
        LoopChange = not GetDictionary('Loop', Message.guild.id)
        ChangeDictionary('Loop', LoopChange, ID)
        await Message.reply(f"Loop set to {LoopChange}")
    elif Command.find(Prefix + 'pause') != -1:
        Voice_Client = GetDictionary('VoiceClient', Message.guild.id)
        if Voice_Client and Voice_Client.is_playing():
            await Voice_Client.pause()
    elif Command.find(Prefix + 'send') != -1:
        arg = Message.content.lower().split(' ')[1]
        Channel = await Client.fetch_channel(arg)
        bla = Message.content.lower().split(' ')
        await Channel.send(" ".join(bla[2:len(bla)]))
        




Client.run('ODk3NDc3MjYyNzIxNTYwNjM3.Gw23Ki.a2XenkHt4Ke5h0aeGxKAmkQuBmAl8visgdavPg')
        