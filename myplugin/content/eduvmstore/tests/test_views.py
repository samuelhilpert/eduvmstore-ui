import sys
from unittest import mock

# Mock all unavailable OpenStack / Horizon modules
sys.modules['horizon'] = mock.MagicMock()
sys.modules['horizon.tabs'] = mock.MagicMock()
sys.modules['horizon.exceptions'] = mock.MagicMock()
sys.modules['openstack_dashboard'] = mock.MagicMock()
sys.modules['openstack_dashboard.api'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.glance'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.nova'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.neutron'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.cinder'] = mock.MagicMock()
sys.modules['openstack_dashboard.api.keystone'] = mock.MagicMock()

# Minimal Django-Settings initialisieren
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test',
        USE_I18N=True,
        USE_L10N=True,
        USE_TZ=True,
        LANGUAGE_CODE='en-us',
        TIME_ZONE='UTC',
        INSTALLED_APPS=[],
    )
    django.setup()

import pytest
import json
from django.http import JsonResponse, HttpResponse
from django.test import RequestFactory
from myplugin.content.eduvmstore import views

@pytest.fixture
def fake_request():
    request = mock.MagicMock()
    request.user = mock.MagicMock()
    request.user.token = mock.MagicMock()
    request.user.token.id = 'fake-token-id'
    request.user.token.user = {'id': 'fake-user-id'}
    request.user.tenant_id = 'fake-tenant-id'
    request.GET = {}
    request.POST = {}
    request.session = {}
    request.method = 'GET'
    request.headers = {}
    return request

@mock.patch('myplugin.content.eduvmstore.views.requests.get')
def test_fetch_app_templates_success(mock_get, fake_request):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{'id': '1'}]
    result = views.fetch_app_templates(fake_request)
    assert result == [{'id': '1'}]
    mock_get.assert_called_once()



@mock.patch('myplugin.content.eduvmstore.views.requests.get')
def test_search_app_templates(mock_get, fake_request):
    fake_request.GET = {'search': 'test'}
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{'id': 'x'}]
    result = views.search_app_templates(fake_request)
    assert result == [{'id': 'x'}]

@mock.patch('myplugin.content.eduvmstore.views.requests.get')
def test_fetch_favorite_app_templates(mock_get, fake_request):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{'favorite': True}]
    result = views.fetch_favorite_app_templates(fake_request)
    assert result == [{'favorite': True}]

@mock.patch('myplugin.content.eduvmstore.views.requests.get')
def test_validate_name_valid(mock_get, fake_request):
    fake_request.method = 'POST'
    fake_request.body = json.dumps({'name': 'my-template'})
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {'collision': False, 'reason': 'ok'}
    response = views.validate_name(fake_request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    assert json.loads(response.content)['valid'] is True

def test_validate_name_invalid_method(fake_request):
    fake_request.method = 'GET'
    response = views.validate_name(fake_request)
    assert response.status_code == 400

def test_format_description():
    text = "some    messy     text"
    result = views.InstancesView().format_description(text)
    assert result == "some messy text"

def test_generate_pdf():
    accounts = [{'username': 'user1', 'password': 'pass1'}]
    instantiations = [{'os': 'linux'}]
    content = views.generate_pdf(accounts, 'test_instance', 'test_template', '2024-01-01', instantiations)
    assert isinstance(content, bytes)

def test_generate_cloud_config():
    accounts = [{'user': 'alice'}]
    instantiations = [{'hostname': 'vm1'}]
    backend_script = '# run backend task'
    content = views.generate_cloud_config(accounts, backend_script, instantiations)
    assert 'cloud-config' in content
    assert '/etc/users.txt' in content

def test_indexview_get_context_data():
    view = views.IndexView()
    view.request = mock.MagicMock()
    with mock.patch('myplugin.content.eduvmstore.views.search_app_templates', return_value=[]), \
            mock.patch('myplugin.content.eduvmstore.views.fetch_favorite_app_templates', return_value=[]), \
            mock.patch.object(view, 'get_images_data', return_value={}):
        context = view.get_context_data()
        assert 'app_templates' in context
        assert 'favorite_app_templates' in context
        assert 'favorite_template_ids' in context

def test_createview_get_context_data():
    view = views.CreateView()
    view.request = mock.MagicMock()
    view.kwargs = {}
    with mock.patch.object(view, 'get_images_data', return_value=[]), \
            mock.patch.object(view, 'get_security_groups', return_value=[]):
        context = view.get_context_data()
        assert 'images' in context
        assert 'security_groups' in context

def test_detailsview_get_context_data():
    view = views.DetailsPageView()
    view.request = mock.MagicMock()
    view.kwargs = {'template_id': '1'}
    with mock.patch.object(view, 'get_app_template', return_value={
        'image_id': 'img1', 'created_at': '2024-01-01T00:00:00', 'creator_id': '1234'}), \
            mock.patch.object(view, 'get_image_data', return_value={'visibility': 'public', 'owner': 'admin'}), \
            mock.patch.object(view, 'get_username_from_id', return_value='admin'):
        context = view.get_context_data()
        assert 'app_template' in context
        assert 'image_visibility' in context
        assert 'image_owner' in context
        assert 'app_template_creator' in context
        assert 'created_at' in context

@mock.patch('myplugin.content.eduvmstore.views.EditView.get_security_groups', return_value=['default'])
@mock.patch('myplugin.content.eduvmstore.views.EditView.get_image_data', return_value={'visibility': 'public', 'owner': 'admin'})
@mock.patch('myplugin.content.eduvmstore.views.EditView.get_app_template', return_value={'image_id': 'img1', 'security_groups': [{'name': 'default'}]})
def test_editview_get_context_data(mock_get_security_groups, mock_get_image_data, mock_get_app_template):
    view = views.EditView()
    view.request = mock.MagicMock()
    view.kwargs = {'template_id': '1'}

    # Rufe die Methode get_context_data auf
    context = view.get_context_data()

    # Testen der Kontextelemente
    assert 'app_template' in context
    assert 'image_visibility' in context
    assert 'image_owner' in context
    assert 'security_groups' in context
    assert 'selected_security_groups' in context




def test_instancesview_get_context_data():
    view = views.InstancesView()
    view.request = mock.MagicMock()
    view.kwargs = {'image_id': '123'}
    with mock.patch.object(view, 'get_app_template', return_value={
        'account_attributes': [{'name': 'username'}],
        'instantiation_attributes': [{'name': 'hostname'}],
        'volume_size_gb': 1
    }), \
            mock.patch.object(view, 'get_flavors', return_value={}), \
            mock.patch.object(view, 'get_networks', return_value={}), \
            mock.patch('myplugin.content.eduvmstore.views.cinder.volume_list', return_value=[]):
        context = view.get_context_data()
        assert 'app_template' in context
        assert 'flavors' in context
        assert 'networks' in context
        assert 'expected_account_fields' in context
        assert 'expected_instantiation_fields' in context
        assert 'volume_size' in context
        assert 'attachable_volumes' in context
        assert 'hasAttachableVolumes' in context

@mock.patch('myplugin.content.eduvmstore.views.socket.socket')
def test_get_host_ip_success(mock_socket_class):
    mock_socket = mock.Mock()
    mock_socket.getsockname.return_value = ['127.0.0.1']
    mock_socket_class.return_value = mock_socket

    import myplugin.content.eduvmstore.views as views
    result = views.get_host_ip()
    assert result == '127.0.0.1'
    mock_socket.connect.assert_called_once_with(("8.8.8.8", 80))
    mock_socket.close.assert_called_once()



@mock.patch('myplugin.content.eduvmstore.views.socket.socket')
def test_get_host_ip_failure(mock_socket_class):
    mock_socket = mock.Mock()
    mock_socket.connect.side_effect = Exception("fail")
    mock_socket_class.return_value = mock_socket

    from myplugin.content.eduvmstore import views

    with pytest.raises(RuntimeError, match="Failed to retrieve host IP address"):
        views.get_host_ip()



def test_get_token_id():
    request = mock.MagicMock()
    request.user.token.id = 'my-token'
    from myplugin.content.eduvmstore import views
    result = views.get_token_id(request)
    assert result == 'my-token'

def test_generate_indented_content():
    text = "line1\nline2"
    result = views.generate_indented_content(text)
    assert result == "      line1\n      line2"

def test_extract_accounts_from_form_new():
    view = views.InstancesView()
    view.request = mock.MagicMock()
    view.kwargs = {'image_id': 'dummy'}

    # Korrektes Setzen der Liste der Benutzernamen
    post_data = QueryDict('', mutable=True)
    post_data.setlist('username_1', ['user1'])  # Korrekt: nur user1 für index 0
    post_data.setlist('username_2', ['user2'])  # Korrekt: nur user2 für index 1
    view.request.POST = post_data

    with mock.patch.object(view, 'get_expected_fields', return_value=['username']):
        result = view.extract_accounts_from_form_new(view.request, 0)

    assert result == [
        {'username': 'user1'},
        {'username': 'user2'}
    ]









def test_get_expected_fields():
    view = views.InstancesView()
    view.request = mock.MagicMock()
    view.expected_fields_raw = [{'name': 'x'}]

    # Setze explizit 'kwargs', damit 'get_app_template' korrekt aufgerufen werden kann.
    view.kwargs = {'image_id': 'dummy-id'}

    # Mock für get_app_template sicherstellen, dass es ein Dictionary mit account_attributes zurückgibt.
    with mock.patch.object(view, 'get_app_template', return_value={'account_attributes': [{'name': 'x'}]}):
        result = view.get_expected_fields()

    # Überprüfe, dass das Ergebnis das Präfix 'account_0_' hat.
    assert result == ['account_0_x']




def test_get_expected_fields_instantiation():
    view = views.InstancesView()
    view.request = mock.MagicMock()
    view.expected_fields_raw = [{'name': 'y'}]
    result = view.get_expected_fields()
    assert result == ['vm_0_y']

@mock.patch('myplugin.content.eduvmstore.views.nova.flavor_list')
def test_get_flavors(mock_flavor_list):
    mock_flavor_list.return_value = [{'name': 'small'}]
    view = views.InstancesView()
    view.request = mock.MagicMock()
    mock_app_template = {'some': 'value'}
    result = view.get_flavors(mock_app_template)
    assert result == [{'name': 'small'}]


@mock.patch('myplugin.content.eduvmstore.views.neutron.network_list')
def test_get_networks(mock_network_list):
    mock_network_list.return_value = [{'name': 'net1'}]
    view = views.InstancesView()
    view.request = mock.MagicMock()
    result = view.get_networks()
    assert result == [{'name': 'net1'}]


@mock.patch('myplugin.content.eduvmstore.views.cinder.volume_get')
def test_wait_for_volume_available(mock_volume_get):
    mock_volume_get.side_effect = [
        mock.Mock(status='creating'),
        mock.Mock(status='available')
    ]

    view = views.InstancesView()
    mock_request = mock.MagicMock()
    view.request = mock_request

    volume = view.wait_for_volume_available(mock_request, 'vol-123')

    assert volume.status == 'available'
    assert mock_volume_get.call_count == 2



@mock.patch('myplugin.content.eduvmstore.views.render')
def test_createview_get(mock_render):
    view = views.CreateView()
    view.request = mock.MagicMock()
    with mock.patch.object(view, 'get_context_data', return_value={'key': 'value'}):
        view.get(view.request)
        mock_render.assert_called_once_with(view.request, 'eduvmstore_dashboard/eduvmstore/create.html', {'key': 'value'})


from django.http import QueryDict

def test_createview_post():
    view = views.CreateView()
    request = mock.MagicMock()

    # Simuliere request.POST als QueryDict, damit .getlist() funktioniert
    post_data = QueryDict('', mutable=True)
    post_data.update({
        'name': 'template',
        'instantiation_attributes': '',
        'account_attributes': '',
        'volume_size': '',
        'security_groups': ['default']
    })
    request.POST = post_data
    request.FILES = {}
    request.user.token = mock.MagicMock()
    request.user.token.id = 'token-id'
    request.user.tenant_id = 'tenant-id'
    view.request = request

    # Mock das Formular
    form_instance = mock.MagicMock()
    form_instance.is_valid.return_value = True
    form_instance.cleaned_data = {'name': 'template'}
    view.get_form_class = mock.MagicMock(return_value=mock.MagicMock(return_value=form_instance))

    # Mock redirect und reverse, um das Django-URL-Setup zu umgehen
    with mock.patch('myplugin.content.eduvmstore.views.redirect') as mock_redirect, \
            mock.patch('myplugin.content.eduvmstore.views.reverse', return_value='/dummy-url'):

        result = view.post(request)

        mock_redirect.assert_called_once_with('/dummy-url')




@mock.patch('myplugin.content.eduvmstore.views.render')
def test_editview_get(mock_render):
    view = views.EditView()
    view.request = mock.MagicMock()
    with mock.patch.object(view, 'get_context_data', return_value={'key': 'val'}):
        view.get(view.request)
        mock_render.assert_called_once_with(view.request, 'eduvmstore_dashboard/eduvmstore/edit.html', {'key': 'val'})



def test_editview_post():
    view = views.EditView()
    request = mock.MagicMock()

    post_data = QueryDict('', mutable=True)
    post_data.setlist('security_groups', ['default'])  # wichtig!
    post_data['name'] = 'template-edited'
    request.POST = post_data
    request.FILES = {}
    request.user.token.id = 'token-id'
    view.request = request
    view.kwargs = {'template_id': '123'}

    form_instance = mock.MagicMock()
    form_instance.is_valid.return_value = True
    form_instance.cleaned_data = {'name': 'template-edited'}

    view.get_form_class = mock.MagicMock(return_value=mock.MagicMock(return_value=form_instance))

    with mock.patch('myplugin.content.eduvmstore.views.redirect') as mock_redirect, \
            mock.patch('myplugin.content.eduvmstore.views.reverse', return_value='/dummy-url'), \
            mock.patch('myplugin.content.eduvmstore.views.requests.put') as mock_put:

        mock_put.return_value.status_code = 200

        result = view.post(request)

        mock_redirect.assert_called_once_with('/dummy-url')

@mock.patch('myplugin.content.eduvmstore.views.render')
def test_instance_success_view_get(mock_render):
    view = views.InstanceSuccessView()
    view.request = mock.MagicMock()
    view.request.GET = {'message': 'Done'}

    view.get(view.request)

    mock_render.assert_called_once_with(
        view.request,
        'eduvmstore_dashboard/eduvmstore/success.html'
    )




import zipfile
import io
from unittest import mock
from django.http import HttpResponse

def test_instance_success_view_post_zip_response():
    view = views.InstanceSuccessView()
    request = mock.MagicMock()
    request.POST = {'as_zip': 'true'}
    view.request = request

    view.request.session = {
        'accounts_1': [{'username': 'user1'}],
        'names_1': 'TestInstance',
        'app_template': 'MyTemplate',
        'created': 'Today',
        'instantiations_1': [{'hostname': 'host1'}],
        'num_instances': 1,
        'base_name': 'test',
        'separate_keys': False,
        'private_key': 'FAKE_KEY',
        'keypair_name': 'testkey',
    }

    with mock.patch('myplugin.content.eduvmstore.views.generate_pdf', return_value=b'%PDF-1.4 dummy'):
        response = view.post(request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/zip'

    zip_data = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_data, 'r') as zip_file:
        file_list = zip_file.namelist()
        assert 'TestInstance.pdf' in file_list
        assert 'testkey.pem' in file_list

        pdf_content = zip_file.read('TestInstance.pdf')
        pem_content = zip_file.read('testkey.pem')

        assert b'%PDF-1.4 dummy' == pdf_content
        assert b'FAKE_KEY' == pem_content



@mock.patch('myplugin.content.eduvmstore.views.redirect', return_value=JsonResponse({'status': 'ok'}))
@mock.patch('myplugin.content.eduvmstore.views.requests.delete')
def test_delete_template_view_post(mock_delete, mock_redirect):
    mock_delete.return_value.status_code = 204
    request = mock.MagicMock()
    request.user.token.id = 'token'

    view = views.DeleteTemplateView()
    view.request = request
    view.kwargs = {'template_id': '1'}

    response = view.post(request, template_id='1')

    assert isinstance(response, JsonResponse)
    assert response.status_code == 200
    mock_redirect.assert_called_once()


@mock.patch('myplugin.content.eduvmstore.views.redirect', return_value=JsonResponse({'id': '123'}))
@mock.patch('myplugin.content.eduvmstore.views.requests.post')
def test_get_favorite_app_template_view_post(mock_post, mock_redirect):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'id': '123'}

    request = mock.MagicMock()
    request.POST = {'template_id': '1'}
    request.user.token.id = 'token'
    request.user.tenant_id = 'tenant'

    view = views.GetFavoriteAppTemplateView()
    view.request = request

    response = view.post(request)

    assert isinstance(response, JsonResponse)
    assert json.loads(response.content)['id'] == '123'
    mock_redirect.assert_called_once()


@mock.patch('myplugin.content.eduvmstore.views.requests.delete')
def test_delete_favorite_app_template_view_post(mock_delete):
    mock_delete.return_value.status_code = 204
    request = mock.MagicMock()
    request.POST = {'template_id': '1'}
    request.user.token.id = 'token'
    request.user.tenant_id = 'tenant'
    view = views.DeleteFavoriteAppTemplateView()
    view.request = request

    response = view.post(request)
    assert isinstance(response, JsonResponse)
    assert response.status_code == 200