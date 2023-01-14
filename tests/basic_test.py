import pyodbc
import requests
import pytest

from unittest.mock import MagicMock
from song_operations import add_song_to_db, get_songs_from_db, connection_string, get_song_by_id_from_db, \
    delete_song_by_id_from_db, update_song_by_id_to_db


@pytest.mark.parametrize("songs,expected",
                         [(('1', 'Abba', 'Mamma Mia'), [{'ID': '1', 'Artist': 'Abba', 'Name': 'Mamma Mia'}])])
def test_get_songs(songs, expected):
    mock_cursor = MagicMock()
    mock_cursor.configure_mock(
        **{
            "fetchall.return_value": [songs],
            "description": (("ID",), ("Artist",), ("Name",))
        }
    )
    actual = get_songs_from_db(mock_cursor)
    assert actual == expected


def test_add_song_to_db():
    mock_cursor = MagicMock()
    song = {'Name': 'Mamma Mia', 'Artist': 'Abba'}
    add_song_to_db(mock_cursor, song)
    mock_cursor.execute.assert_called_with('INSERT INTO [dbo].[Song] (Name, Artist) VALUES (?, ?)', 'Mamma Mia', 'Abba')
    mock_cursor.commit.assert_called()


@pytest.mark.parametrize("songs,expected",
                         [([('1', 'Abba', 'Mamma Mia')], [{'ID': '1', 'Artist': 'Abba', 'Name': 'Mamma Mia'}]),([] ,[])])
def test_get_song_by_id_from_db(songs, expected):
    mock_cursor = MagicMock()
    mock_cursor.configure_mock(
        **{
            "fetchall.return_value": songs,
            "description": (("ID",), ("Artist",), ("Name",))
        }
    )
    actual = get_song_by_id_from_db(mock_cursor, '1')
    mock_cursor.execute.assert_called_with("SELECT * from [dbo].[Song] song where song.id=?", '1')
    assert actual == expected


def test_delete_song_from_db():
    mock_cursor = MagicMock()
    song_id = '1'
    delete_song_by_id_from_db(mock_cursor, song_id)
    mock_cursor.execute.assert_called_with('DELETE FROM [dbo].[Song] WHERE ID=?', '1')
    mock_cursor.commit.assert_called()


def test_update_song_to_db():
    mock_cursor = MagicMock()
    song_id = '1'
    song = {'Name': 'Mamma Mia', 'Artist': 'Abba'}
    update_song_by_id_to_db(mock_cursor, song, song_id)
    mock_cursor.execute.assert_called_with('UPDATE [dbo].[Song] SET Name=?, Artist=? WHERE ID=?', 'Mamma Mia', 'Abba', '1')
    mock_cursor.commit.assert_called()


def test_db_connection():
    connection = pyodbc.connect(connection_string)
    assert connection is not None


def test_main_route():
    session = requests.Session()
    response = session.get("https://project-lesniak.azurewebsites.net/")
    session.close()
    assert "Sign In" in str(response.content)
