def test_api_key(api_key):
    assert api_key == "test_api_key"


def test_channel_handle(channel_handle):
    assert channel_handle == "MRCHEESE"


def test_postgres_connection(mock_postgres_connection):
    assert mock_postgres_connection.login == "test_user"
    assert mock_postgres_connection.password == "test_password"
    assert mock_postgres_connection.host == "localhost"
    assert mock_postgres_connection.port == 5432
    assert mock_postgres_connection.schema == "test_db"
