import unittest
from unittest.mock import patch, Mock
from django.test import RequestFactory
import json
from django.http import JsonResponse
from myplugin.content.eduvmstore.views import (
    validate_name,
    GetFavoriteAppTemplateView,
    DeleteFavoriteAppTemplateView,
    DeleteTemplateView,
)


class EduVMStoreNonContentViewTests(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("myplugin.content.eduvmstore.views.requests.get")
    @patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
    def test_validate_name_valid(self, mock_token, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'collision': False,
            'reason': 'Name already taken'
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        request = self.factory.post("/", content_type="application/json", data='{"name": "test"}')
        response = validate_name(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"valid": True, "reason": "Name already taken"})




    @patch("myplugin.content.eduvmstore.views.redirect")
    @patch("myplugin.content.eduvmstore.views.requests.post")
    @patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.eduvmstore.views.messages")
    def test_get_favorite_app_template_success(self, mock_messages, mock_token, mock_post, mock_redirect):
        request = self.factory.post("/", {"template_id": "123", "template_name": "Ubuntu"})
        request.user = Mock()
        mock_post.return_value.status_code = 201

        GetFavoriteAppTemplateView.as_view()(request)

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called_once()

    @patch("myplugin.content.eduvmstore.views.redirect")
    @patch("myplugin.content.eduvmstore.views.requests.delete")
    @patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.eduvmstore.views.messages")
    def test_delete_favorite_app_template_success(self, mock_messages, mock_token, mock_delete, mock_redirect):
        request = self.factory.post("/", {"template_id": "123", "template_name": "Ubuntu"})
        request.user = Mock()
        mock_delete.return_value.status_code = 204

        DeleteFavoriteAppTemplateView.as_view()(request)

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called_once()

    @patch("myplugin.content.eduvmstore.views.redirect")
    @patch("myplugin.content.eduvmstore.views.requests.delete")
    @patch("myplugin.content.eduvmstore.views.requests.get")
    @patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
    @patch("myplugin.content.eduvmstore.views.messages")
    def test_delete_template_success(self, mock_messages, mock_token, mock_get, mock_delete, mock_redirect):
        request = self.factory.post("/", {"template_name": "Ubuntu"})
        request.user = Mock()
        request.user.token.user = {'id': 'abc123'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'creator_id': 'abc123'}
        mock_delete.return_value.status_code = 204

        DeleteTemplateView.as_view()(request, template_id="123")

        mock_messages.success.assert_called_once()
        mock_redirect.assert_called()

