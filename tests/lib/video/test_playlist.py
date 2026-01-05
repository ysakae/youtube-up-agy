import unittest
from unittest.mock import MagicMock
from src.lib.video.playlist import PlaylistManager

class TestPlaylistManager(unittest.TestCase):
    def setUp(self):
        self.mock_service = MagicMock()
        self.manager = PlaylistManager(self.mock_service)
        
        # Mock playlists().list().execute()
        self.mock_list = self.mock_service.playlists().list.return_value
        self.mock_list.execute.return_value = {
            "items": [
                {"id": "PL123", "snippet": {"title": "Existing Playlist"}}
            ]
        }
        
        # Mock playlists().insert().execute()
        self.mock_insert = self.mock_service.playlists().insert.return_value
        self.mock_insert.execute.return_value = {"id": "PL_NEW", "snippet": {"title": "New Playlist"}}

    def test_get_or_create_existing(self):
        playlist_id = self.manager.get_or_create_playlist("Existing Playlist")
        self.assertEqual(playlist_id, "PL123")
        # specific args verification omitted for brevity, checking logic flow
        
    def test_get_or_create_new(self):
        playlist_id = self.manager.get_or_create_playlist("New Playlist")
        self.assertEqual(playlist_id, "PL_NEW")
        self.mock_service.playlists().insert.assert_called()

    def test_add_video_to_playlist(self):
        # Mock successful add
        self.mock_service.playlistItems().insert.return_value.execute.return_value = {}
        
        success = self.manager.add_video_to_playlist("PL123", "VID999")
        self.assertTrue(success)
        self.mock_service.playlistItems().insert.assert_called()

if __name__ == '__main__':
    unittest.main()
