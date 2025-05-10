import pytest
import requests
from unittest import mock
from django.test import RequestFactory
from myplugin.content.eduvmstore.view.apptemplate import AppTemplateView


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def post_data():
    return {
        'image_id': 'img-123',
        'name': 'New Template',
        'description': 'A test template',
        'short_description': 'Short',
        'instantiation_notice': 'Note',
        'public': 'True',
        'hiddenScriptField': '#!/bin/bash\necho Hello',
        'ssh_user_requested': 'on',
        'instantiation_attributes': 'attr1:attr2',
        'account_attributes': 'acc1:acc2',
        'version': '1.0',
        'volume_size': '5',
        'fixed_ram_gb': '2',
        'fixed_disk_gb': '10',
        'fixed_cores': '1',
        'security_groups': ['default', 'web']
    }


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.reverse", return_value="/dummy-redirect/")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.redirect", side_effect=lambda url: url)
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_token_id", return_value="test-token")
@mock.patch("requests.post")
def test_post_create_success(mock_requests_post, mock_get_token, mock_redirect, mock_reverse, post_data):
    mock_requests_post.return_value.status_code = 201
    request = RequestFactory().post('/create', data=post_data)
    request.resolver_match = mock.Mock(url_name='create')
    request.user = mock.Mock()
    request._messages = mock.Mock()

    view = AppTemplateView()
    view.setup(request)
    view.mode = "create"

    response = view.post(request)

    assert response == "/dummy-redirect/"


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.redirect", side_effect=lambda url: url)
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.reverse", return_value="/dummy-redirect/")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_token_id", return_value="test-token")
@mock.patch("requests.post")
def test_post_create_failure(mock_post, mock_get_token, mock_reverse, mock_redirect, request_factory,
                             post_data):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    request = request_factory.post('/create', data=post_data)
    request.resolver_match = mock.Mock(url_name='create')
    request.user = mock.Mock()
    request._messages = mock.Mock()

    view = AppTemplateView()
    view.setup(request)
    view.mode = "create"

    response = view.post(request)

    assert response == "/dummy-redirect/"
    mock_post.assert_called_once()


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.redirect", side_effect=lambda url: url)
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.reverse", return_value="/dummy-redirect/")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_token_id", return_value="test-token")
@mock.patch("requests.post", side_effect=requests.exceptions.RequestException("Timeout"))
def test_post_create_exception(mock_post, mock_get_token, mock_reverse, mock_redirect, request_factory,
                               post_data):
    request = request_factory.post('/create', data=post_data)
    request.resolver_match = mock.Mock(url_name='create')
    request.user = mock.Mock()
    request._messages = mock.Mock()

    view = AppTemplateView()
    view.setup(request)
    view.mode = "create"

    response = view.post(request)

    assert response == "/dummy-redirect/"


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_images_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_image_data",
            return_value={"visibility": "public", "owner": "admin"})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_app_template",
            return_value={"image_id": "img-123", "security_groups": [{"name": "default"}]})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.neutron.security_group_list", return_value=[])
def test_get_context_data_with_template_id(mock_sec, mock_get_template, mock_image_data, mock_images,
                                           request_factory):
    request = request_factory.get('/create')
    request.GET = {}
    request.user = mock.Mock()
    request.resolver_match = mock.Mock(url_name='edit')

    view = AppTemplateView()
    view.setup(request, template_id='123')
    view.mode = "edit"

    context = view.get_context_data()

    assert context['app_template'] is not None
    assert context['image_visibility'] == 'public'
    assert context['image_owner'] == 'admin'
    assert context['is_edit'] is True


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_app_template",
            return_value={"image_id": "img-123", "security_groups": []})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_image_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_images_data", return_value={})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.neutron.security_group_list",
            side_effect=Exception("Neutron error"))
def test_get_context_data_security_group_exception(mock_sec, *_):
    request = RequestFactory().get('/create')
    request.GET = {}
    request.user = mock.Mock()
    request.resolver_match = mock.Mock(url_name='edit')

    view = AppTemplateView()
    view.setup(request, template_id='123')
    view.mode = "create"
    context = view.get_context_data()

    assert context['security_groups'] == []


@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_token_id", return_value="test-token")
@mock.patch("requests.put")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.reverse", return_value="/dummy-redirect/")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.redirect", side_effect=lambda url: url)
def test_post_edit_failure(mock_redirect, mock_reverse, mock_put, mock_get_token, request_factory, post_data):
    mock_put.return_value.status_code = 500
    mock_put.return_value.text = "Internal Server Error"

    request = request_factory.post('/edit/123', data=post_data)
    request.resolver_match = mock.Mock(url_name='edit')
    request.user = mock.Mock()
    request._messages = mock.Mock()

    view = AppTemplateView()
    view.setup(request, template_id='123')
    view.mode = "edit"

    response = view.post(request)

    assert response == "/dummy-redirect/"
    mock_put.assert_called_once()


def test_get_context_data_invalid_template_name(request_factory):
    request = request_factory.get('/create', data={'template': 'unknown'})
    request.GET = {'template': 'unknown'}
    request.user = mock.Mock()
    request.resolver_match = mock.Mock(url_name='create')

    view = AppTemplateView()
    view.setup(request)
    view.mode = "create"

    context = view.get_context_data()

    assert context['app_template'] == {}
    assert context['security_groups'] == []
