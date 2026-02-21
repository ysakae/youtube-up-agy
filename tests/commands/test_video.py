import unittest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from src.main import app

runner = CliRunner()

class TestVideoCommand(unittest.TestCase):
    
    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    @patch("src.commands.video.PlaylistManager")
    def test_update_privacy_bulk_success(self, MockPlaylistManager, MockVideoManager, mock_get_credentials):
        # Setup
        mock_creds = MagicMock()
        mock_get_credentials.return_value = mock_creds
        
        mock_idx_mgr = MockVideoManager.return_value
        mock_idx_mgr.update_privacy_status.return_value = True
        
        mock_pl_mgr = MockPlaylistManager.return_value
        mock_pl_mgr.get_video_ids_from_playlist.return_value = ["vid1", "vid2"]
        
        # Execute
        result = runner.invoke(app, ["video", "update-privacy", "all", "unlisted", "--playlist", "MyPlaylist"])
        
        # Verify
        if result.exit_code != 0:
            print(result.output)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Bulk Update Complete", result.stdout)
        self.assertIn("vid1", result.stdout)
        
        mock_pl_mgr.get_video_ids_from_playlist.assert_called_with("MyPlaylist")
        self.assertEqual(mock_idx_mgr.update_privacy_status.call_count, 2)

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_update_privacy_single_success(self, MockVideoManager, mock_get_credentials):
        mock_creds = MagicMock()
        mock_get_credentials.return_value = mock_creds
        
        mock_idx_mgr = MockVideoManager.return_value
        mock_idx_mgr.update_privacy_status.return_value = True
        
        result = runner.invoke(app, ["video", "update-privacy", "VID123", "public"])
        
        if result.exit_code != 0:
            print(result.output)
        self.assertEqual(result.exit_code, 0)
        mock_idx_mgr.update_privacy_status.assert_called_with("VID123", "public")

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_update_metadata_single_success(self, MockVideoManager, mock_get_credentials):
         mock_creds = MagicMock()
         mock_get_credentials.return_value = mock_creds
         
         mock_idx_mgr = MockVideoManager.return_value
         mock_idx_mgr.update_metadata.return_value = True
         
         result = runner.invoke(app, ["video", "update-meta", "VID123", "--title", "New Title"])
         
         if result.exit_code != 0:
            print(result.output)
         self.assertEqual(result.exit_code, 0)
         mock_idx_mgr.update_metadata.assert_called_with(
             "VID123", title="New Title", description=None, tags=None, category_id=None
         )

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_update_thumbnail_success(self, MockVideoManager, mock_get_credentials):
         mock_creds = MagicMock()
         mock_get_credentials.return_value = mock_creds
         
         mock_idx_mgr = MockVideoManager.return_value
         mock_idx_mgr.update_thumbnail.return_value = True
         
         result = runner.invoke(app, ["video", "update-thumbnail", "VID123", "./thumb.jpg"])
         
         self.assertEqual(result.exit_code, 0)
         mock_idx_mgr.update_thumbnail.assert_called_with("VID123", "./thumb.jpg")

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_delete_video_success(self, MockVideoManager, mock_get_credentials):
         mock_creds = MagicMock()
         mock_get_credentials.return_value = mock_creds
         
         mock_idx_mgr = MockVideoManager.return_value
         mock_idx_mgr.delete_video.return_value = True
         
         # Test with -y option to skip prompt
         result = runner.invoke(app, ["video", "delete-video", "VID123", "-y"])
         
         self.assertEqual(result.exit_code, 0)
         mock_idx_mgr.delete_video.assert_called_with("VID123")

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_list_videos(self, MockVideoManager, mock_get_credentials):
        """video list の正常系テスト"""
        mock_get_credentials.return_value = MagicMock()
        mock_mgr = MockVideoManager.return_value
        mock_mgr.get_all_uploaded_videos.return_value = [
            {"id": "vid1", "title": "Video One", "privacy": "private"},
            {"id": "vid2", "title": "Video Two", "privacy": "public"},
        ]

        result = runner.invoke(app, ["video", "list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Video One", result.output)
        self.assertIn("Video Two", result.output)
        mock_mgr.get_all_uploaded_videos.assert_called_once()

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_list_videos_with_status_filter(self, MockVideoManager, mock_get_credentials):
        """video list --status フィルタテスト"""
        mock_get_credentials.return_value = MagicMock()
        mock_mgr = MockVideoManager.return_value
        mock_mgr.get_all_uploaded_videos.return_value = [
            {"id": "vid1", "title": "Private Video", "privacy": "private"},
            {"id": "vid2", "title": "Public Video", "privacy": "public"},
        ]

        result = runner.invoke(app, ["video", "list", "--status", "public"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Public Video", result.output)
        # private のものは表示されないはず（フィルタ済み）

    @patch("src.commands.video.get_credentials")
    @patch("src.commands.video.VideoManager")
    def test_list_videos_empty(self, MockVideoManager, mock_get_credentials):
        """動画0件の場合のテスト"""
        mock_get_credentials.return_value = MagicMock()
        mock_mgr = MockVideoManager.return_value
        mock_mgr.get_all_uploaded_videos.return_value = []

        result = runner.invoke(app, ["video", "list"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No uploaded videos found", result.output)

if __name__ == "__main__":
    unittest.main()
