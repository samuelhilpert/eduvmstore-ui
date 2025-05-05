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

