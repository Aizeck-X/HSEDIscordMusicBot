import discord
from discord.ext import commands
import wavelink
from config import token

client = commands.Bot(command_prefix="!!", intents=discord.Intents.all())

class CustomPlayer(wavelink.Player):

    """
    This class represents a custom player that extends the functionality of the wavelink.Player class.

    Attributes:
    - queue (wavelink.Queue): A queue object used for managing the playback queue.

    Methods:
    - __init__(): Initializes the CustomPlayer object and sets up the queue.

    """
    
    def __init__(self):
        super().__init__()
        self.queue = wavelink.Queue()

# helper function
@client.event
async def on_node():
        
    """
    This function is an event handler that is triggered when a node is connected.
    It connects to a Wavelink node using the specified URI and password, and sets the autoplay option to True.

    Parameters:
    None

    Returns:
    None
    """
    
    node: wavelink.Node = wavelink.Node._connect(uri="lavalink.oryzen.xyz:80", password="oryzen.xyz", client=client)
    wavelink.player.autoplay = True

# events
@client.event
async def on_wavelink_node_ready(node: wavelink.Node):

    """
    This function is an event handler that is triggered when a Wavelink node is ready.
    It prints a message indicating that the node with its identifier is ready.

    Parameters:
    - node (wavelink.Node): The Wavelink node that is ready.

    Returns:
    None
    """

    print(f"Node: <{node.identifier}> is ready!")


@client.event
async def on_wavelink_track_end(player: CustomPlayer, track: wavelink.tracks, reason):

    """
    This function is an event handler that is triggered when a Wavelink track ends.
    If the player's queue is not empty, it retrieves the next track from the queue and plays it.

    Parameters:
    - player (CustomPlayer): The Wavelink player.
    - track (wavelink.tracks): The track that has ended.
    - reason: The reason for the track ending.

    Returns:
    None
    """

    if not player.queue.is_empty:
        next_track = player.queue.get()
        await player.play(next_track)


@client.event
async def on_ready():

    """
    This function is an event handler that is triggered when the bot is ready.
    It prints a message indicating that the bot is ready.

    Parameters:
    None

    Returns:
    None
    """

    print("Bot ready")


# commands
@client.command()
async def stop(ctx):

    """
    This command stops the player and disconnects the bot from the voice channel.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    
    Returns:
    None
    """
    
    vc = ctx.voice_client
    if vc:
        await vc.disconnect()
        await ctx.send_message(f"🎶 The player has stopped and the queue has been cleared.")

@client.command()
async def play(ctx, *, search: str):

    """
    This command plays a song or adds it to the queue if there is already a song playing.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    - search (str): The search query for the song to be played.
    
    Returns:
    None
    """

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

    """
    This command skips the currently playing song and plays the next song in the queue.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    
    Returns:
    None
    """
    
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
    
    """
    This command changes the volume of the currently playing song.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    - volume (int): The desired volume level (0-100).
    
    Returns:
    None
    """

    if (ctx.voice_client is None):
        return await ctx.send_message(f"🚫 There must be music playing to use that!")
    
    await ctx.send_message(f"🔈 Volume changed from {ctx.voice_client.source.volume} to {volume / 100}")
    ctx.voice_client.source.volume = volume / 100

@client.command()
async def repeat(ctx):

    """
    This command toggles the repeat mode on or off.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    
    Returns:
    None
    """

    if loop:
        await ctx.send('🎶 Repeat mode is now `Off`')
        loop = False
    
    else: 
        await ctx.send('🎶 Repeat mode is now `All`')
        loop = True
    
@client.command()
async def queue(ctx):

    """
    This command displays the current song queue.
    
    Parameters:
    - ctx (discord.ext.commands.Context): The context of the command.
    
    Returns:
    None
    """

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