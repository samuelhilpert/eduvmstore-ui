import pytest
import json
from unittest import mock
from django.test import RequestFactory
from django.http import QueryDict
from myplugin.content.eduvmstore.view.apptemplate import AppTemplateView
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpResponse



@pytest.fixture
def factory():
    return RequestFactory()

def add_messages_middleware(request):
    """Hilfsfunktion, um message middleware zu simulieren."""
    setattr(request, '_messages', FallbackStorage(request))

from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test.client import RequestFactory

def get_mock_request(method='GET', data=None):
    request = RequestFactory().generic(method, '/dummy-url', data=data)
    request.user = mock.MagicMock()
    request.user.token = mock.MagicMock(id='fake-token')
    request.resolver_match = mock.MagicMock()
    request.resolver_match.url_name = 'create'

    # Session Middleware anwenden – OHNE save()
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)

    # Messages Middleware simulieren
    request._messages = FallbackStorage(request)

    return request



@mock.patch("myplugin.content.eduvmstore.view.apptemplate.render")
def test_get_renders_template(mock_render, factory):
    request = get_mock_request('GET')
    view = AppTemplateView()
    view.setup(request)
    view.mode = 'create'
    response = view.get(request)
    mock_render.assert_called_once()

@mock.patch("myplugin.content.eduvmstore.view.apptemplate.requests.post")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.messages")
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.reverse", return_value='/redirect-url')
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.redirect", return_value=HttpResponse("OK"))
def test_post_create_success(mock_redirect, mock_reverse, mock_messages, mock_post):
    post_data = {
        'image_id': 'img-123',
        'name': 'Test Template',
        'description': 'desc',
        'short_description': 'short',
        'instantiation_notice': 'notice',
        'public': 'true',
        'hiddenScriptField': '#!/bin/bash',
        'ssh_user_requested': 'on',
        'instantiation_attributes': 'hostname',
        'account_attributes': 'username',
        'version': '1.0',
        'volume_size': '5',
        'fixed_ram_gb': '2',
        'fixed_disk_gb': '20',
        'fixed_cores': '1',
        'security_groups': ['default']
    }

    request = get_mock_request('POST', data=post_data)
    request.POST = QueryDict('', mutable=True)
    request.POST.update(post_data)

    view = AppTemplateView()
    view.setup(request)
    view.mode = 'create'

    mock_post.return_value.status_code = 201  # Jetzt korrekt

    response = view.post(request)
    mock_messages.success.assert_called_once()
    assert response.status_code == 200

group = mock.Mock()
group.name = 'default'
group.id = 'sg1'

@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_app_template", return_value={'image_id': 'img1', 'security_groups': [{'name': 'default'}]})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_image_data", return_value={'visibility': 'public', 'owner': 'admin'})
@mock.patch("myplugin.content.eduvmstore.view.apptemplate.neutron.security_group_list", return_value=[group])
def test_get_context_data_edit(mock_sg_list, mock_img_data, mock_template):
    image_mock = mock.Mock()
    image_mock.id = 'img1'
    image_mock.name = 'Image 1'

    with mock.patch("myplugin.content.eduvmstore.view.apptemplate.get_images_data", return_value={'img1': image_mock}):
        request = get_mock_request()
        view = AppTemplateView()
        view.request = request
        view.kwargs = {'template_id': '123'}
        view.mode = 'edit'

        context = view.get_context_data()

        assert context['app_template']['image_id'] == 'img1'
        assert context['image_visibility'] == 'public'
        assert context['security_groups'][0]['selected'] is True
        assert context['images'][0] == ('img1', 'Image 1')
