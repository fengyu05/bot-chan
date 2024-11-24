# pylint: disable=redefined-outer-name,protected-access
from unittest.mock import AsyncMock, Mock, patch

import pytest
from discord import DMChannel, Message, TextChannel, Thread

from fluctlight.discord.bot_client import DiscordBotClient
from fluctlight.discord.discord_bot_proxy import DiscordBotProxy

DISCORD_BOT_DEVELOPER_ROLE = "developer"


@pytest.fixture
def mock_discord_bot_proxy():
    bot_proxy = DiscordBotProxy()
    bot_proxy.set_bot_client(Mock(spec=DiscordBotClient))
    bot_proxy.client.user = Mock(id=123, mentioned_in=Mock(return_value=False))

    return bot_proxy


@pytest.fixture
def mock_message():
    message = Mock(spec=Message)
    message.author.id = 456  # Different from bot user id to simulate another user
    message.content = "Hello"
    message.channel = Mock(spec=TextChannel)  # Default to text channel

    return message


@pytest.fixture
def mock_dm_message(mock_message: Message):
    mock_message.channel = Mock(spec=DMChannel)
    mock_message.channel.recipient = Mock(id=456)

    return mock_message


@pytest.fixture
def mock_member_with_developer_role():
    role = Mock()
    role.name = DISCORD_BOT_DEVELOPER_ROLE
    member = Mock()
    member.roles = [role]
    return member


@pytest.fixture
def mock_thread_message(mock_message: Message):
    mock_message.channel = Mock(spec=Thread)
    mock_message.channel.owner_id = 123  # Same as bot user id

    return mock_message


@pytest.mark.asyncio
async def test_is_trust_dm_with_developer_role(
    mock_discord_bot_proxy, mock_dm_message, mock_member_with_developer_role
):
    with patch.object(
        mock_discord_bot_proxy,
        "get_message_author_member",
        return_value=mock_member_with_developer_role,
    ):
        is_trust_dm = mock_discord_bot_proxy._is_trust_dm(mock_dm_message)
        assert is_trust_dm is True


@pytest.mark.asyncio
async def test_is_trust_dm_without_developer_role(
    mock_discord_bot_proxy, mock_dm_message
):
    # Mock member with no roles or different roles
    mock_member = Mock()
    mock_member.roles = []

    with patch.object(
        mock_discord_bot_proxy, "get_message_author_member", return_value=mock_member
    ):
        is_trust_dm = mock_discord_bot_proxy._is_trust_dm(mock_dm_message)
        assert is_trust_dm is False


@pytest.mark.asyncio
async def test_should_reply_if_mentioned(
    mock_discord_bot_proxy: DiscordBotProxy, mock_message: Message
):
    mock_discord_bot_proxy.client.user.mentioned_in.return_value = True
    should_reply = mock_discord_bot_proxy._should_reply(mock_message)
    assert should_reply is True


@pytest.mark.asyncio
async def test_should_reply_in_thread(
    mock_discord_bot_proxy: DiscordBotProxy, mock_thread_message: Message
):
    should_reply = mock_discord_bot_proxy._should_reply(mock_thread_message)
    assert should_reply is True
