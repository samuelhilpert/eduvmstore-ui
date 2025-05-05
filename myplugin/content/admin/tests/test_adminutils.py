import unittest
from unittest.mock import patch, Mock
from myplugin.content.admin.utils import (
    get_users,
    get_roles,
    get_user_details,
    get_app_templates_to_approve,
    get_app_templates,
)

class TestUtils(unittest.TestCase):

    @patch("myplugin.content.admin.utils.requests.get")
    def test_get_users(self, mock_get):
        request = Mock()
        request.user.token.id = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "1", "name": "user1"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        self.assertEqual(get_users(request), [{"id": "1", "name": "user1"}])

    @patch("myplugin.content.admin.utils.requests.get")
    def test_get_roles(self, mock_get):
        request = Mock()
        request.user.token.id = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "1", "name": "role1"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        self.assertEqual(get_roles(request), [{"id": "1", "name": "role1"}])

    @patch("myplugin.content.admin.utils.requests.get")
    def test_get_user_details(self, mock_get):
        request = Mock()
        request.user.token.id = "test_token"
        user_id = "123"
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "user1"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        self.assertEqual(get_user_details(request, user_id), {"id": "123", "name": "user1"})

    @patch("myplugin.content.admin.utils.requests.get")
    def test_get_app_templates_to_approve(self, mock_get):
        request = Mock()
        request.user.token.id = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "1", "name": "template1"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        self.assertEqual(get_app_templates_to_approve(request), [{"id": "1", "name": "template1"}])

    @patch("myplugin.content.admin.utils.requests.get")
    def test_get_app_templates(self, mock_get):
        request = Mock()
        request.user.token.id = "test_token"
        mock_response = Mock()
        mock_response.json.return_value = [{"id": "1", "name": "template1"}]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        self.assertEqual(get_app_templates(request), [{"id": "1", "name": "template1"}])

