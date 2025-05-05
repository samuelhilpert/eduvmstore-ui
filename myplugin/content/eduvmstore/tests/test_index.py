import pytest
from unittest import mock
from django.test import RequestFactory
from myplugin.content.eduvmstore.view.index import IndexView
from django.http import HttpResponse
from django.views import generic



@pytest.fixture
def mock_request():
    request = RequestFactory().get('/dummy-url')
    request.user = mock.Mock()
    request.headers = {}
    return request


@mock.patch("myplugin.content.eduvmstore.view.index.get_images_data")
@mock.patch("myplugin.content.eduvmstore.view.index.fetch_favorite_app_templates")
@mock.patch("myplugin.content.eduvmstore.view.index.search_app_templates")
def test_get_context_data_with_images(mock_search, mock_favorites, mock_images, mock_request):
    # Setup mock data
    mock_search.return_value = [{'id': '1', 'image_id': 'img-1'}, {'id': '2', 'image_id': 'img-2'}]
    mock_favorites.return_value = [{'id': '1', 'image_id': 'img-1'}]

    image_1 = mock.Mock()
    image_1.size = 104857600  # 100 MB
    image_1.visibility = 'public'

    image_2 = mock.Mock()
    image_2.size = 52428800  # 50 MB
    image_2.visibility = 'private'

    mock_images.return_value = {
        'img-1': image_1,
        'img-2': image_2
    }

    view = IndexView()
    view.request = mock_request
    context = view.get_context_data()

    assert len(context['app_templates']) == 2
    assert context['app_templates'][0]['size'] == 100.0
    assert context['app_templates'][1]['size'] == 50.0
    assert context['favorite_app_templates'][0]['visibility'] == 'public'
    assert context['favorite_template_ids'] == ['1']
    assert context['page_title'] == "EduVMStore Dashboard"


@mock.patch("myplugin.content.eduvmstore.view.index.get_images_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.index.fetch_favorite_app_templates", return_value=[])
@mock.patch("myplugin.content.eduvmstore.view.index.search_app_templates", return_value=[])
def test_get_context_data_empty(mock_search, mock_favorites, mock_images, mock_request):
    view = IndexView()
    view.request = mock_request
    context = view.get_context_data()

    assert context['app_templates'] == []
    assert context['favorite_app_templates'] == []
    assert context['favorite_template_ids'] == []
    assert context['page_title'] == "EduVMStore Dashboard"


@mock.patch("myplugin.content.eduvmstore.view.index.render", return_value=HttpResponse("AJAX OK"))
@mock.patch("myplugin.content.eduvmstore.view.index.IndexView.get_context_data", return_value={'data': 'context'})
def test_get_ajax_returns_partial(mock_get_context, mock_render, mock_request):
    mock_request.headers['X-Requested-With'] = 'XMLHttpRequest'

    view = IndexView()
    view.request = mock_request
    response = view.get(mock_request)

    mock_render.assert_called_once_with(mock_request, "eduvmstore_dashboard/eduvmstore/table.html", {'data': 'context'})
    assert response.status_code == 200
    assert response.content == b"AJAX OK"


@mock.patch("myplugin.content.eduvmstore.view.index.IndexView.get_context_data", return_value={'page_title': 'Test'})
def test_get_standard_request_calls_super(mock_get_context, mock_request):
    view = IndexView()
    view.request = mock_request

    # Wir patchen `super().get` mit einem Mock
    with mock.patch.object(generic.TemplateView, "get", return_value=HttpResponse("FULL OK")) as super_get:
        response = view.get(mock_request)

    super_get.assert_called_once_with(mock_request)
    assert response.status_code == 200
    assert response.content == b"FULL OK"
