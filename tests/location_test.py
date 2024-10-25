import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../develop')))

import pytest
from unittest.mock import AsyncMock, Mock, patch
from develop.location_manager import LocationManager
from develop.database_manager import DatabaseManager
from telegram import Update, Message, User, Location, Chat, CallbackQuery
from telegram.ext import CallbackContext


@pytest.mark.asyncio
async def test_update_location_command():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/update_location")
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    location_manager = LocationManager(db_manager=db_manager)

    message.reply_text = AsyncMock()

    await location_manager.update_location_command(update, context)

    message.reply_text.assert_called_once_with(
        "Пожалуйста, отправьте свою геолокацию для обновления. Нажмите на иконку скрепки и выберите 'Геолокация'."
    )


@pytest.mark.asyncio
async def test_update_location_command():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/update_location")
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    location_manager = LocationManager(db_manager=db_manager)

    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        await location_manager.update_location_command(update, context)

        mock_reply.assert_called_once_with(
            "Пожалуйста, отправьте свою геолокацию для обновления. Нажмите на иконку скрепки и выберите 'Геолокация'."
        )


@pytest.mark.asyncio
async def test_update_location_success():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    location = Location(latitude=55.7558, longitude=37.6173)
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text=None, location=location)
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    location_manager = LocationManager(db_manager=db_manager)

    db_manager.update_user_location = Mock()

    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        await location_manager.update_location(update, context)

        db_manager.update_user_location.assert_called_once_with("@testuser", 55.7558, 37.6173)
        mock_reply.assert_called_once_with("Геолокация обновлена: 55.7558, 37.6173")


@pytest.mark.asyncio
async def test_update_location_no_location():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/update_location")
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    location_manager = LocationManager(db_manager=db_manager)

    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        await location_manager.update_location(update, context)

        mock_reply.assert_called_once_with(
            "Не удалось получить геолокацию. Убедитесь, что вы разрешили доступ к геолокации и попробуйте снова."
        )

@pytest.mark.asyncio
async def test_show_current_location_success():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/show_location")
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    db_manager.get_user_location = Mock(return_value=(55.7558, 37.6173))

    location_manager = LocationManager(db_manager=db_manager)

    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        await location_manager.show_current_location(update, context)

        db_manager.get_user_location.assert_called_once_with("@testuser")
        mock_reply.assert_called_once_with("Текущая геолокация: 55.7558, 37.6173")

@pytest.mark.asyncio
async def test_show_current_location_no_data():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)
    chat = Chat(id=12345, type='private')
    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/show_location")
    update = Update(update_id=1, message=message)
    context = Mock(spec=CallbackContext)

    db_manager = Mock(spec=DatabaseManager)
    db_manager.get_user_location = Mock(return_value=None)

    location_manager = LocationManager(db_manager=db_manager)

    with patch.object(Message, 'reply_text', new=AsyncMock()) as mock_reply:
        await location_manager.show_current_location(update, context)

        db_manager.get_user_location.assert_called_once_with("@testuser")
        mock_reply.assert_called_once_with("Геолокация пока не установлена.")