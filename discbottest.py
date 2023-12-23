import pytest
from unittest.mock import patch, Mock, AsyncMock
from discord.ext import commands
from discbot3 import CustomPlayer, play

@pytest.fixture
def bot():
    return commands.Bot(command_prefix="!!", intents=discord.Intents.all())

@pytest.fixture
def ctx():
    mock_ctx = AsyncMock(spec=commands.Context)
    mock_ctx.author.voice.channel.connect = AsyncMock()

    mock_ctx.voice_client = None

    return mock_ctx

@pytest.mark.asyncio
async def test_play_command_no_voice_client(bot, ctx):
    with patch('discbot3.wavelink.Playable.search') as mock_search, \
            patch('discbot3.CustomPlayer') as mock_custom_player:
        
        mock_custom_player.return_value.is_playing.return_value = False
        mock_custom_player.return_value.play = AsyncMock()

        mock_search_result = Mock()
        mock_search_result.title = "Test Song"
        mock_search_result.uri = "http://testsonguri.com"
        mock_search.return_value = mock_search_result

        ctx.author.voice.channel.connect.return_value = mock_custom_player.return_value
        
        await bot.add_command(play)
        await bot.get_command('play')(ctx, search='Test Song')

        mock_custom_player.assert_called_once()
        ctx.author.voice.channel.connect.assert_awaited_once_with(cls=CustomPlayer)

        mock_custom_player.return_value.play.assert_awaited_once_with('Test Song')

        assert ctx.send_message.call_count == 1
        args, kwargs = ctx.send_message.call_args
        embed = kwargs['embed']
        assert embed.title == "Test Song"
        assert embed.description == f"Playing Test Song in {ctx.author.voice.channel}"

async def test_queue_command_with_songs(ctx):
    fake_queue = [MagicMock(title="Song 1"), MagicMock(title="Song 2"), MagicMock(title="Song 3")]
    
    ctx.voice_client.queue.is_empty = False
    ctx.voice_client.queue.copy.return_value = fake_queue
    
    await client.get_command('queue')(ctx)
    
    ctx.send_message.assert_awaited_once()
  
    _, kwargs = ctx.send_message.call_args
    embed_sent = kwargs.get('embed', None)
    assert embed_sent.title == "Queue"
    assert all(f"{song.title}" in embed_sent.fields[i].value for i, song in enumerate(fake_queue))

@pytest.mark.asyncio
async def test_queue_command_empty(ctx):
    ctx.voice_client.queue.is_empty = True

    await client.get_command('queue')(ctx)

    ctx.send_message.assert_awaited_once_with("🚫 There must be music playing to use that!")
