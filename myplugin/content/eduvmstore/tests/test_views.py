import unittest
from unittest.mock import patch, Mock
from django.test import RequestFactory
import json
import requests
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

@patch("myplugin.content.eduvmstore.views.requests.get", side_effect=requests.RequestException("API down"))
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
def test_validate_name_api_failure(mock_token, mock_get):
    request = RequestFactory().post("/", content_type="application/json", data='{"name": "test"}')
    response = validate_name(request)
    assert response.status_code == 200
    assert json.loads(response.content) == {"valid": False, "reason": "Name already taken"}


@patch("myplugin.content.eduvmstore.views.requests.get")
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
def test_validate_name_invalid_json(mock_token, mock_get):
    request = RequestFactory().post("/", content_type="application/json", data="invalid_json")
    response = validate_name(request)
    assert response.status_code == 200
    assert json.loads(response.content) == {"valid": False, "reason": "Name already taken"}


@patch("myplugin.content.eduvmstore.views.redirect")
@patch("myplugin.content.eduvmstore.views.requests.post")
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
@patch("myplugin.content.eduvmstore.views.messages")
def test_get_favorite_app_template_failure(mock_messages, mock_token, mock_post, mock_redirect):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"error": "Invalid data"}

    request = RequestFactory().post("/", {"template_id": "123", "template_name": "Test"})
    request.user = Mock()

    GetFavoriteAppTemplateView.as_view()(request)
    mock_messages.error.assert_called_once()


@patch("myplugin.content.eduvmstore.views.redirect")
@patch("myplugin.content.eduvmstore.views.requests.delete")
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
@patch("myplugin.content.eduvmstore.views.messages")
def test_delete_favorite_app_template_failure(mock_messages, mock_token, mock_delete, mock_redirect):
    mock_delete.return_value.status_code = 400
    mock_delete.return_value.json.return_value = {"error": "Invalid request"}

    request = RequestFactory().post("/", {"template_id": "123", "template_name": "Test"})
    request.user = Mock()

    DeleteFavoriteAppTemplateView.as_view()(request)
    mock_messages.error.assert_called_once()


@patch("myplugin.content.eduvmstore.views.requests.get")
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
@patch("myplugin.content.eduvmstore.views.messages")
@patch("myplugin.content.eduvmstore.views.redirect")
def test_delete_template_unauthorized(mock_redirect, mock_messages, mock_token, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"creator_id": "someone-else"}

    request = RequestFactory().post("/", {"template_name": "Test"})
    request.user = Mock()
    request.user.token.user = {"id": "not-the-owner"}

    DeleteTemplateView.as_view()(request, template_id="123")

    mock_messages.error.assert_called_with(request, "You are not authorized to delete this template.")


@patch("myplugin.content.eduvmstore.views.requests.get")
@patch("myplugin.content.eduvmstore.views.requests.delete")
@patch("myplugin.content.eduvmstore.views.get_token_id", return_value="test_token")
@patch("myplugin.content.eduvmstore.views.messages")
@patch("myplugin.content.eduvmstore.views.redirect")
def test_delete_template_api_delete_failed(mock_redirect, mock_messages, mock_token, mock_delete, mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"creator_id": "abc"}
    mock_delete.return_value.status_code = 400
    mock_delete.return_value.json.return_value = {"error": "Deletion failed"}

    request = RequestFactory().post("/", {"template_name": "Test"})
    request.user = Mock()
    request.user.token.user = {"id": "abc"}

    DeleteTemplateView.as_view()(request, template_id="123")

    mock_messages.error.assert_called_once()
