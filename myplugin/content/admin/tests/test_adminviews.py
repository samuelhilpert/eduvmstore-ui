import unittest
from unittest.mock import patch, Mock
from django.test import RequestFactory

from myplugin.content.admin.views import (
    UpdateRolesView,
    ApproveTemplateView,
    RejectTemplateView,
    DeleteTemplateView,
    DeleteUserView,
)

class AdminActionViewsTest(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("myplugin.content.admin.views.redirect")
    @patch("myplugin.content.admin.views.requests.patch")
    @patch("myplugin.content.admin.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.admin.views.messages")
    def test_update_roles_success(self, mock_messages, mock_token, mock_patch, mock_redirect):
        request = self.factory.post("/", {"user_id": "123", "new_role_id": "456"})
        request.user = Mock()
        mock_patch.return_value.status_code = 200

        UpdateRolesView.as_view()(request)

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called_once()


    @patch("myplugin.content.admin.views.redirect")
    @patch("myplugin.content.admin.views.requests.patch")
    @patch("myplugin.content.admin.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.admin.views.messages")
    def test_reject_template_success(self, mock_messages, mock_token, mock_patch, mock_redirect):
        request = self.factory.post("/", {"template_id": "42"})
        request.user = Mock()
        mock_patch.return_value.status_code = 200

        RejectTemplateView.as_view()(request)

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called_once()

    @patch("myplugin.content.admin.views.redirect")
    @patch("myplugin.content.admin.views.requests.delete")
    @patch("myplugin.content.admin.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.admin.views.messages")
    def test_delete_template_success(self, mock_messages, mock_token, mock_delete, mock_redirect):
        request = self.factory.post("/", {"template_id": "template123"})
        request.user = Mock()
        mock_delete.return_value.status_code = 204

        DeleteTemplateView.as_view()(request)

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called_once()


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.messages")
def test_update_roles_missing_fields(mock_messages, mock_redirect):
    request = RequestFactory().post("/", {})  # keine Daten
    request.user = Mock()

    UpdateRolesView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "User ID and Role ID are required.")
    mock_redirect.assert_called_once()


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.requests.patch")
@patch("myplugin.content.admin.views.get_token_id", return_value="test_token")
@patch("myplugin.content.admin.views.messages")
def test_update_roles_api_error(mock_messages, mock_token, mock_patch, mock_redirect):
    request = RequestFactory().post("/", {"user_id": "123", "new_role_id": "456"})
    request.user = Mock()
    mock_patch.return_value.status_code = 400
    mock_patch.return_value.json.return_value = {"error": "Invalid role ID"}

    UpdateRolesView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "Failed to update role: Invalid role ID")


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.messages")
def test_approve_template_missing_id(mock_messages, mock_redirect):
    request = RequestFactory().post("/", {})  # fehlt template_id
    request.user = Mock()

    ApproveTemplateView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "App Template ID is required.")


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.requests.patch")
@patch("myplugin.content.admin.views.get_token_id", return_value="token")
@patch("myplugin.content.admin.views.messages")
def test_reject_template_api_error(mock_messages, mock_token, mock_patch, mock_redirect):
    request = RequestFactory().post("/", {"template_id": "42"})
    request.user = Mock()
    mock_patch.return_value.status_code = 403
    mock_patch.return_value.json.return_value = {"error": "Not authorized"}

    RejectTemplateView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "Failed to reject app template: Not authorized")


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.requests.delete")
@patch("myplugin.content.admin.views.get_token_id", return_value="token")
@patch("myplugin.content.admin.views.messages")
def test_delete_template_api_error(mock_messages, mock_token, mock_delete, mock_redirect):
    request = RequestFactory().post("/", {"template_id": "fail42"})
    request.user = Mock()
    mock_delete.return_value.status_code = 500
    mock_delete.return_value.json.return_value = {"error": "Server error"}

    DeleteTemplateView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "Failed to delete template: Server error")


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.messages")
def test_delete_user_missing_id(mock_messages, mock_redirect):
    request = RequestFactory().post("/", {})  # kein user_id
    request.user = Mock()

    DeleteUserView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "Template ID is required.")


@patch("myplugin.content.admin.views.redirect")
@patch("myplugin.content.admin.views.requests.delete")
@patch("myplugin.content.admin.views.get_token_id", return_value="token")
@patch("myplugin.content.admin.views.messages")
def test_delete_user_api_error(mock_messages, mock_token, mock_delete, mock_redirect):
    request = RequestFactory().post("/", {"user_id": "broken"})
    request.user = Mock()
    mock_delete.return_value.status_code = 403
    mock_delete.return_value.json.return_value = {"error": "Permission denied"}

    DeleteUserView.as_view()(request)

    mock_messages.error.assert_called_once_with(request, "Failed to delete user: Permission denied")
