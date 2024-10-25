import pytest
from unittest.mock import patch, Mock
from develop.database_manager import DatabaseManager


@pytest.fixture
def db_manager():
    with patch('psycopg2.connect') as mock_connect:
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        db_manager = DatabaseManager(db_name="testdb", user="testuser", password="testpass")
        yield db_manager
        db_manager.close()


def test_add_user(db_manager):
    db_manager.add_user("testuser")

    db_manager.cursor.execute.assert_called_once_with(
        "INSERT INTO public.users (username) VALUES (%s) ON CONFLICT (username) DO NOTHING;",
        ("testuser",)
    )
    db_manager.connection.commit.assert_called_once()


def test_add_user_exception(db_manager):
    db_manager.cursor.execute.side_effect = Exception("Database error")

    db_manager.add_user("testuser")

    db_manager.connection.rollback.assert_called_once()


def test_update_user_location(db_manager):
    db_manager.update_user_location("testuser", 55.7558, 37.6173)

    db_manager.cursor.execute.assert_called_once_with(
        "UPDATE public.users SET latitude = %s, longitude = %s WHERE username = %s;",
        (55.7558, 37.6173, "testuser")
    )
    db_manager.connection.commit.assert_called_once()


def test_update_user_location_exception(db_manager):
    db_manager.cursor.execute.side_effect = Exception("Database error")

    db_manager.update_user_location("testuser", 55.7558, 37.6173)

    db_manager.connection.rollback.assert_called_once()


def test_get_user_location(db_manager):
    db_manager.cursor.fetchone.return_value = (55.7558, 37.6173)

    result = db_manager.get_user_location("testuser")

    assert result == (55.7558, 37.6173)
    db_manager.cursor.execute.assert_called_once_with(
        "SELECT latitude, longitude FROM public.users WHERE username = %s;",
        ("testuser",)
    )


def test_get_user_location_no_data(db_manager):
    db_manager.cursor.fetchone.return_value = None

    result = db_manager.get_user_location("unknown_user")

    assert result is None


def test_get_all_users(db_manager):
    db_manager.cursor.fetchall.return_value = [("user1", 55.7558, 37.6173), ("user2", 51.5074, -0.1278)]

    result = db_manager.get_all_users()

    assert result == [("user1", 55.7558, 37.6173), ("user2", 51.5074, -0.1278)]
    db_manager.cursor.execute.assert_called_once_with("SELECT * FROM users;")


def test_get_all_users_exception(db_manager):
    db_manager.cursor.execute.side_effect = Exception("Database error")

    result = db_manager.get_all_users()

    assert result == []
