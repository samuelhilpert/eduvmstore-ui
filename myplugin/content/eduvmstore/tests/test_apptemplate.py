import pytest
from unittest import mock
from django.test import RequestFactory
from myplugin.content.eduvmstore.view.detail import DetailsPageView


@pytest.fixture
def mock_request():
    req = RequestFactory().get('/dummy-url')
    req.user = mock.Mock()
    return req


@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get")
@mock.patch("myplugin.content.eduvmstore.view.detail.get_image_data")
@mock.patch("myplugin.content.eduvmstore.view.detail.get_app_template")
def test_context_data_success(mock_get_template, mock_get_image, mock_user_get, mock_request):
    mock_get_template.return_value = {
        'name': 'Test Template',
        'image_id': 'img-123',
        'creator_id': 'abc-def',
        'created_at': '2024-01-01T12:34:56'
    }
    mock_get_image.return_value = {
        'visibility': 'public',
        'owner': 'admin'
    }
    mock_user = mock.Mock()
    mock_user.name = 'user123'
    mock_user_get.return_value = mock_user

    view = DetailsPageView()
    view.setup(mock_request, template_id='123')

    context = view.get_context_data()

    assert context['app_template']['name'] == 'Test Template'
    assert context['image_visibility'] == 'public'
    assert context['image_owner'] == 'admin'
    assert context['app_template_creator'] == 'user123'
    assert context['created_at'] == '2024-01-01'
    assert context['page_title'] == 'Test Template'


@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get", side_effect=Exception("not found"))
@mock.patch("myplugin.content.eduvmstore.view.detail.get_image_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.detail.get_app_template")
def test_context_data_user_get_fails(mock_get_template, mock_get_image, mock_user_get, mock_request):
    mock_get_template.return_value = {
        'name': 'Broken Template',
        'image_id': 'img-999',
        'creator_id': '123-456',
        'created_at': '2023-11-11T10:00:00'
    }

    view = DetailsPageView()
    view.setup(mock_request, template_id='broken123')

    context = view.get_context_data()

    assert context['app_template_creator'] == '123456'
    assert context['image_visibility'] == 'N/A'
    assert context['image_owner'] == 'N/A'
    assert context['created_at'] == '2023-11-11'
    assert context['page_title'] == 'Broken Template'


@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get")
@mock.patch("myplugin.content.eduvmstore.view.detail.get_image_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.detail.get_app_template")
def test_context_data_creator_id_missing(mock_get_template, mock_get_image, mock_user_get, mock_request):
    mock_get_template.return_value = {
        'name': 'Nameless Template',
        'image_id': 'img-000',
        'created_at': '2025-05-05T09:00:00'
    }

    view = DetailsPageView()
    view.setup(mock_request, template_id='no_creator')

    context = view.get_context_data()

    assert context['app_template_creator'] == 'N/A'
    assert context['created_at'] == '2025-05-05'
    assert context['page_title'] == 'Nameless Template'


@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get")
@mock.patch("myplugin.content.eduvmstore.view.detail.get_image_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.detail.get_app_template")
def test_context_data_created_at_missing(mock_get_template, mock_get_image, mock_user_get, mock_request):
    mock_get_template.return_value = {
        'name': 'Old Template',
        'image_id': 'img-456',
        'creator_id': 'creator-id-abc'
    }

    mock_user = mock.Mock()
    mock_user.name = 'creator_user'
    mock_user_get.return_value = mock_user

    view = DetailsPageView()
    view.setup(mock_request, template_id='no_date')

    context = view.get_context_data()

    assert context['created_at'] == ''
    assert context['app_template_creator'] == 'creator_user'
    assert context['page_title'] == 'Old Template'



@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get")
def test_get_username_from_id_success(mock_user_get, mock_request):
    mock_user = mock.Mock()
    mock_user.name = 'alice'
    mock_user_get.return_value = mock_user

    view = DetailsPageView()
    view.request = mock_request

    result = view.get_username_from_id('abc123')
    assert result == 'alice'


@mock.patch("myplugin.content.eduvmstore.view.detail.keystone.user_get", side_effect=Exception("not found"))
def test_get_username_from_id_fallback(mock_user_get, mock_request):
    view = DetailsPageView()
    view.request = mock_request

    result = view.get_username_from_id('abc123')
    assert result == 'abc123'
