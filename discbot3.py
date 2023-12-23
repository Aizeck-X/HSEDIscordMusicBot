import discord
from discord.ext import commands
import wavelink
from config import token

client = commands.Bot(command_prefix="!!", intents=discord.Intents.all())


class CustomPlayer(wavelink.Player):

    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()


# HTTPS and websocket operations
@client.event
async def on_ready():
    print("Bot ready")


# helper function
@client.event
async def on_node():
    
    node: wavelink.Node = wavelink.Node._connect(uri="lavalink.oryzen.xyz:80", password="oryzen.xyz", client=client)
    wavelink.player.autoplay = True


# events

@client.event
async def on_wavelink_node_ready(node: wavelink.Node):
    print(f'Node: <{node.identifier}> is ready!')


@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.tracks, reason):
    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)


# commands

@client.command()
async def stop(ctx):
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send_message(f"🎶 The player has stopped and the queue has been cleared.")

@client.command()
async def play(ctx, *, search: str):

    tracks: wavelink.Search = await wavelink.Playable.search(search)
    
    vc = ctx.voice_client
    if not vc:
        custom_player = CustomPlayer()
        vc: CustomPlayer = await ctx.author.voice.channel.connect(cls=custom_player)

    if vc.is_playing():

        vc.queue.put(item=search)

        await ctx.send_message(embed=discord.Embed(
            title=search.title,
            url=search.uri,
            author=ctx.author,
            description=f"Queued {search.title} in {vc.channel}"
        ))
    else:
        await vc.play(search)

        await ctx.send_message(embed=discord.Embed(
            title=vc.source.title,
            url=vc.source.uri,
            author=ctx.author,
            description=f"Playing {vc.source.title} in {vc.channel}"
        ))


@client.command()
async def skip(ctx):
    vc = ctx.voice_client
    if vc:
        if not vc.is_playing():
            return await ctx.send_message(f"🎶 Skipped {vc.source.title}")
        if vc.queue.is_empty:
            await ctx.send_message(f"🚫 There must be music playing to use that!")
            return await vc.stop()

        await vc.seek(vc.track.length * 1000)
        if vc.is_paused():
            await vc.resume()
    else:
        await ctx.send_message(f"The bot is not connected to a voice channel.")

@client.command()
async def volume(ctx, volume: int):
    if (ctx.voice_client is None):
        return await ctx.send_message(f"🚫 There must be music playing to use that!")
    
    await ctx.send_message(f"🔈 Volume changed from {ctx.voice_client.source.volume} to {volume / 100}")
    ctx.voice_client.source.volume = volume / 100


@client.command()
async def repeat(ctx):

    if loop:
        await ctx.send('🎶 Repeat mode is now `Off`')
        loop = False
    
    else: 
        await ctx.send('🎶 Repeat mode is now `All`')
        loop = True
    

@client.command()
async def queue(ctx):

    vc = ctx.voice_client

    if not vc.queue.is_empty:

        song_counter = 0
        songs = []
        queue = vc.queue.copy()
        embed = discord.Embed(title="Queue")

        for song in queue:

            song_counter +=1
            songs.append(song)
            embed.add_field(name=f"[{song_counter}]", value=f"{song.title}", inline=True)
        
        await ctx.send_message(embed)
    else:
        await ctx.send_message(f"🚫 There must be music playing to use that!")


client.run(token)