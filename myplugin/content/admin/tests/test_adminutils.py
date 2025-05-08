import unittest
import requests
from unittest.mock import patch, Mock
from myplugin.content.admin.utils import (
    get_users,
    get_roles,
    get_user_details,
    get_app_templates_to_approve,
    get_app_templates,
    get_username_from_id,
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


@patch("myplugin.content.admin.utils.requests.get",
       side_effect=requests.RequestException("Connection failed"))
def test_get_users_failure(mock_get):
    request = Mock()
    request.user.token.id = "test_token"
    result = get_users(request)
    assert result == []


@patch("myplugin.content.admin.utils.requests.get", side_effect=requests.RequestException("Timeout"))
def test_get_roles_failure(mock_get):
    request = Mock()
    request.user.token.id = "test_token"
    result = get_roles(request)
    assert result == []


@patch("myplugin.content.admin.utils.requests.get", side_effect=requests.RequestException("Server error"))
def test_get_user_details_failure(mock_get):
    request = Mock()
    request.user.token.id = "test_token"
    result = get_user_details(request, "user-id")
    assert result == {}


@patch("myplugin.content.admin.utils.requests.get",
       side_effect=requests.RequestException("API not reachable"))
def test_get_app_templates_to_approve_failure(mock_get):
    request = Mock()
    request.user.token.id = "test_token"
    result = get_app_templates_to_approve(request)
    assert result == []


@patch("myplugin.content.admin.utils.requests.get",
       side_effect=requests.RequestException("Internal server error"))
def test_get_app_templates_failure(mock_get):
    request = Mock()
    request.user.token.id = "test_token"
    result = get_app_templates(request)
    assert result == []


@patch("myplugin.content.admin.utils.keystone.user_get", side_effect=Exception("Keystone down"))
def test_get_username_from_id_failure(mock_user_get):
    request = Mock()
    result = get_username_from_id(request, "user-id-123")
    assert result == "user-id-123"
