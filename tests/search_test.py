import pytest
from unittest.mock import AsyncMock, Mock, patch
from develop.search import Search
from telegram import Update, Message, User, Chat, Bot
from telegram.ext import CallbackContext


@pytest.mark.asyncio
async def test_search_success():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)

    chat = Chat(id=12345, type='private')
    bot = Mock(spec=Bot)

    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/search")
    message._bot = bot

    update = Update(update_id=1, message=message)

    context = Mock(spec=CallbackContext)

    db_manager = Mock()
    db_manager.get_user_location.return_value = (55.7558, 37.6173)

    search = Search(api_key="testkey", db_manager=db_manager)
    search.find_nearest_bars_and_clubs = Mock(return_value="Ближайшие бары и клубы найдены")

    await search.search(update, context)

    search.find_nearest_bars_and_clubs.assert_called_with(55.7558, 37.6173)
    assert search.find_nearest_bars_and_clubs.called


@pytest.mark.asyncio
async def test_search_no_location():
    user = User(id=1, username="testuser", first_name="Test", is_bot=False)

    chat = Chat(id=12345, type='private')
    bot = Mock(spec=Bot)

    message = Message(message_id=1, from_user=user, chat=chat, date=None, text="/search")
    message._bot = bot

    update = Update(update_id=1, message=message)

    context = Mock(spec=CallbackContext)

    db_manager = Mock()
    db_manager.get_user_location.return_value = None

    search = Search(api_key="testkey", db_manager=db_manager)

    await search.search(update, context)

    db_manager.get_user_location.assert_called_with("@testuser")


@pytest.mark.asyncio
async def test_search_for_group_success():
    update = Update(update_id=1, message=AsyncMock())

    context = Mock(spec=CallbackContext)

    db_manager = Mock()
    db_manager.get_all_users.return_value = [(1, "@user1"), (2, "@user2")]
    db_manager.get_user_location.side_effect = [(55.7558, 37.6173), (55.75, 37.62)]

    search = Search(api_key="testkey", db_manager=db_manager)
    search.find_nearest_bars_and_clubs = Mock(return_value="Групповой поиск выполнен успешно")

    await search.search_for_group(update, context)

    search.find_nearest_bars_and_clubs.assert_called_with(55.7529, 37.61865)
    assert search.find_nearest_bars_and_clubs.called


@pytest.mark.asyncio
async def test_search_for_group_no_users():
    update = Update(update_id=1, message=AsyncMock())

    context = Mock(spec=CallbackContext)

    db_manager = Mock()
    db_manager.get_all_users.return_value = []

    search = Search(api_key="testkey", db_manager=db_manager)

    await search.search_for_group(update, context)

    db_manager.get_all_users.assert_called_once()


def test_find_nearest_bars_and_clubs_success():
    search = Search(api_key="testkey", db_manager=None)
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = {
            "result": {
                "items": [
                    {
                        "name": "Бар",
                        "address_name": "Улица",
                        "geometry": {
                            "location": {"lat": 55.7558, "lon": 37.6173}
                        }
                    }
                ]
            }
        }
        mock_get.return_value.raise_for_status = Mock()

        result = search.find_nearest_bars_and_clubs(55.7558, 37.6173)
        assert "Бар" in result


def test_find_nearest_bars_and_clubs_error():
    search = Search(api_key="testkey", db_manager=None)
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Ошибка сети")

        with pytest.raises(Exception) as excinfo:
            search.find_nearest_bars_and_clubs(55.7558, 37.6173)
        assert "Ошибка сети" in str(excinfo.value)


def test_get_coordinates_by_address_success():
    search = Search(api_key="testkey", db_manager=None)
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = [{"lat": "55.7558", "lon": "37.6173"}]
        mock_get.return_value.raise_for_status = Mock()

        result = search._get_coordinates_by_address("Москва")
        assert result == (55.7558, 37.6173)


def test_get_coordinates_by_address_error():
    search = Search(api_key="testkey", db_manager=None)
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Ошибка сети")

        with pytest.raises(Exception) as excinfo:
            search._get_coordinates_by_address("Неизвестный адрес")
        assert "Ошибка сети" in str(excinfo.value)

def test_generate_yandex_maps_link_with_name_success():
    search = Search(api_key="testkey", db_manager=None)
    result = search._generate_yandex_maps_link_with_name("Бар", 55.7558, 37.6173)
    assert "yandex.ru/maps" in result
    assert "55.7558" in result


def test_generate_yandex_maps_link_with_name_empty():
    search = Search(api_key="testkey", db_manager=None)
    result = search._generate_yandex_maps_link_with_name("", 55.7558, 37.6173)
    assert "yandex.ru/maps" in result
