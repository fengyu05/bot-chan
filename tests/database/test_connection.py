import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import sessionmaker
from fluctlight.database.connection import create_session, get_db  # Update with the actual module name
class TestDatabaseFunctions(unittest.TestCase):

    @patch('fluctlight.database.connection.create_engine')
    def test_create_session(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_sessionmaker = MagicMock(return_value=MagicMock())
        mock_create_engine.return_value = mock_engine

        with patch('fluctlight.database.connection.SQLALCHEMY_DATABASE_URL', 'mock_database_url'):
            # Call the function we're testing
            session = create_session()

            # Assert create_engine was called once with the correct URL
            mock_create_engine.assert_called_once_with('mock_database_url', connect_args={})

            # Assert sessionmaker was called correctly
            self.assertIsInstance(session, sessionmaker)


    @patch('fluctlight.database.connection.create_engine')
    def test_create_session_returns_same_object(self, mock_create_engine):
        # Mock the engine and sessionmaker
        mock_engine = MagicMock()
        mock_session_instance = MagicMock()
        
        # Mock the sessionmaker to return the same session instance
        mock_sessionmaker = MagicMock(return_value=mock_session_instance)

        # Set the mocked create_engine to return our mock_engine
        mock_create_engine.return_value = mock_engine

        with patch('fluctlight.database.connection.SQLALCHEMY_DATABASE_URL', 'mock_database_url'):
            # Call create_session for the first time
            session1 = create_session()
            # Call create_session for the second time
            session2 = create_session()

            # Assert both calls return the same session object
            assert session1 is session2, "The two sessions are not the same object"


    @patch('fluctlight.database.connection.create_session')
    def test_get_db(self, mock_create_session):
        mock_db_session = MagicMock()
        mock_create_session.return_value = mock_db_session
        
        with patch('fluctlight.database.connection.USE_SQL_CHAR_DB', True): 
            db_generator = get_db()
            
            # Extract the session from the generator
            db_session = next(db_generator)

            # Assertions to ensure the session was created and closed properly
            self.assertIs(db_session, mock_db_session)
            mock_create_session.assert_called_once()

            # Close the session and check if close method was called
            mock_db_session.close.assert_not_called()  # Not yet closed

            # Finish the generator to trigger finally block
            try:
                next(db_generator)
            except StopIteration:
                pass

            mock_db_session.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
