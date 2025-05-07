import pytest
from unittest import mock
from django.http import QueryDict
from django.test import RequestFactory
from myplugin.content.eduvmstore.view.instances import InstancesView


@pytest.fixture
def mock_request():
    req = RequestFactory().get('/dummy-url')
    req.user = mock.Mock(tenant_id='tenant123')
    req.session = {}
    return req


@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template")
@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_list")
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.get_networks", return_value={'net1': 'Network 1'})
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.get_flavors", return_value={'flavors': {}})
def test_get_context_data(mock_flavors, mock_networks, mock_volume_list, mock_get_template, mock_request):
    mock_get_template.return_value = {
        'name': 'Example',
        'volume_size_gb': 5,
        'account_attributes': [{'name': 'username'}],
        'instantiation_attributes': [{'name': 'hostname'}]
    }
    mock_volume_list.return_value = [mock.Mock(status='available')]

    view = InstancesView()
    view.request = mock_request
    view.kwargs = {'image_id': 'img-123'}
    context = view.get_context_data()

    assert context['app_template_id'] == 'img-123'
    assert context['volume_size'] == 5
    assert context['expected_account_fields'] == ['username']
    assert context['expected_instantiation_fields'] == ['hostname']
    assert context['hasAttachableVolumes'] is True


@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.get_context_data", return_value={'page_title': 'Test'})
@mock.patch("myplugin.content.eduvmstore.view.instances.render")
def test_get_renders_template(mock_render, mock_get_context, mock_request):
    view = InstancesView()
    response = view.get(mock_request)
    mock_render.assert_called_once_with(mock_request, 'eduvmstore_dashboard/eduvmstore/instances.html', {'page_title': 'Test'})

import pytest
from unittest import mock
from django.test import RequestFactory
from django.http import QueryDict
from django.urls import reverse
from myplugin.content.eduvmstore.view.instances import InstancesView
from django.http import HttpResponse


@pytest.fixture
def mock_post_request():
    data = {
        'instance_count': '1',
        'instances_name': 'testvm',
        'flavor_id_1': 'flavor1',
        'network_id_1': 'net1',
        'volume_size_1': '5',
        'user_count_1': '0',
        'use_existing_volume_1': 'new',
        'separate_keys': 'false'
    }

    request = RequestFactory().post('/dummy-url', data=data)
    request.POST = QueryDict('', mutable=True)
    request.POST.update(data)
    request.user = mock.Mock(tenant_id='tenant123')
    request.session = {}
    return request


@mock.patch("myplugin.content.eduvmstore.view.instances.reverse", return_value="/success")
@mock.patch("myplugin.content.eduvmstore.view.instances.redirect", return_value=HttpResponse("Redirected"))
@mock.patch("myplugin.content.eduvmstore.view.instances.nova.server_create")
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.wait_for_ip_in_network", return_value=['10.0.0.5'])
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.wait_for_server")
@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_create")
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.wait_for_volume_available")
@mock.patch("myplugin.content.eduvmstore.view.instances.nova.keypair_list", return_value=[])
@mock.patch("myplugin.content.eduvmstore.view.instances.nova.keypair_create")
@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template")
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.get_network_name_by_id", return_value='net1')
def test_post_success(
        mock_get_network_name,
        mock_get_template,
        mock_keypair_create,
        mock_keypair_list,
        mock_wait_vol,
        mock_volume_create,
        mock_wait_server,
        mock_wait_ip,
        mock_server_create,
        mock_redirect,
        mock_reverse,
        mock_post_request
):
    mock_get_template.return_value = {
        'name': 'TestTemplate',
        'image_id': 'img-123',
        'script': '',
        'description': 'desc',
        'created_at': '2024-01-01T00:00:00',
        'volume_size_gb': 5,
        'ssh_user_requested': False,
        'security_groups': [{'name': 'default'}],
        'account_attributes': [],
        'instantiation_attributes': []
    }

    mock_keypair_create.return_value.private_key = "PRIVATE_KEY"
    mock_volume_create.return_value.id = "vol-123"
    mock_wait_vol.return_value = mock_volume_create.return_value
    mock_wait_server.return_value.id = "server-123"
    mock_server_create.return_value.id = "server-123"

    view = InstancesView()
    view.setup(mock_post_request, image_id="img-123")

    response = view.post(mock_post_request)
    assert response.status_code == 200
    assert response.content == b"Redirected"
    assert mock_redirect.called


@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template", side_effect=Exception("broken"))
@mock.patch("myplugin.content.eduvmstore.view.instances.render", return_value=HttpResponse("ErrorPage"))
@mock.patch("myplugin.content.eduvmstore.view.instances.InstancesView.get_context_data", return_value={})
def test_post_exception_handling(mock_context, mock_render, mock_get_template, mock_post_request):
    view = InstancesView()
    view.setup(mock_post_request, image_id="img-123")
    response = view.post(mock_post_request)
    assert response.status_code == 200
    assert b"ErrorPage" in response.content

@pytest.fixture
def request_with_user():
    request = RequestFactory().get('/')
    request.user = mock.Mock(tenant_id="tenant123")
    return request



@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_type_list", return_value=[])
def test_get_available_volume_types_empty(mock_list, request_with_user):
    view = InstancesView()
    result = view.get_available_volume_types(request_with_user)
    assert result is None


@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_type_list")
def test_get_available_volume_types_success(mock_list, request_with_user):
    vt = mock.Mock(name='voltype1')
    vt.name = 'fast-ssd'
    mock_list.return_value = [vt]

    view = InstancesView()
    result = view.get_available_volume_types(request_with_user)
    assert result == 'fast-ssd'



@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_get")
def test_wait_for_volume_available_ready(mock_get, request_with_user):
    vol = mock.Mock()
    vol.status = 'available'
    mock_get.return_value = vol

    view = InstancesView()
    result = view.wait_for_volume_available(request_with_user, 'vol-id', timeout=1)
    assert result.status == 'available'


@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_get")
def test_wait_for_volume_available_error(mock_get, request_with_user):
    vol = mock.Mock()
    vol.status = 'error'
    mock_get.return_value = vol

    view = InstancesView()
    with pytest.raises(Exception, match="Volume vol-id failed to build."):
        view.wait_for_volume_available(request_with_user, 'vol-id', timeout=1)


@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_get", return_value=mock.Mock(status='building'))
def test_wait_for_volume_available_timeout(mock_get, request_with_user):
    view = InstancesView()
    with pytest.raises(TimeoutError):
        view.wait_for_volume_available(request_with_user, 'vol-id', timeout=1)



@mock.patch("myplugin.content.eduvmstore.view.instances.nova.server_get")
def test_wait_for_server_success(mock_get, request_with_user):
    server = mock.Mock()
    mock_get.return_value = server

    view = InstancesView()
    result = view.wait_for_server(request_with_user, 'srv-id', timeout=1)
    assert result == server


@mock.patch("myplugin.content.eduvmstore.view.instances.nova.server_get", side_effect=Exception("not found"))
def test_wait_for_server_timeout(mock_get, request_with_user):
    view = InstancesView()
    with pytest.raises(Exception, match="Instance srv-id could not be found after 1 seconds."):
        view.wait_for_server(request_with_user, 'srv-id', timeout=1)


@mock.patch("myplugin.content.eduvmstore.view.instances.nova.server_get")
def test_wait_for_ip_success(mock_get, request_with_user):
    mock_get.return_value.addresses = {
        "net1": [{"addr": "192.168.0.10"}]
    }

    view = InstancesView()
    result = view.wait_for_ip_in_network(request_with_user, "srv-id", "net1", timeout=1)
    assert result == "192.168.0.10"


@mock.patch("myplugin.content.eduvmstore.view.instances.nova.server_get", return_value=mock.Mock(addresses={}))
def test_wait_for_ip_timeout(mock_get, request_with_user):
    view = InstancesView()
    result = view.wait_for_ip_in_network(request_with_user, "srv-id", "missingnet", timeout=1)
    assert isinstance(result, list)
    assert "No IP found" in result[0]

@pytest.fixture
def view_instance():
    view = InstancesView()
    request = RequestFactory().get('/')
    request.user = mock.Mock(tenant_id="tenant123")
    request.session = {}
    view.request = request
    view.kwargs = {'image_id': 'img-001'}
    return view



@mock.patch("myplugin.content.eduvmstore.view.instances.nova.flavor_list", return_value=[])
def test_get_flavors_empty(mock_list, view_instance):
    result = view_instance.get_flavors({})
    assert result == {}


@mock.patch("myplugin.content.eduvmstore.view.instances.nova.flavor_list")
def test_get_flavors_success(mock_list, view_instance):
    f1 = mock.Mock()
    f1.id = '1'
    f1.name = 'small'
    f1.ram = 2048
    f1.disk = 20
    f1.vcpus = 1

    f2 = mock.Mock()
    f2.id = '2'
    f2.name = 'medium'
    f2.ram = 4096
    f2.disk = 40
    f2.vcpus = 2

    mock_list.return_value = [f1, f2]

    result = view_instance.get_flavors({})
    assert 'flavors' in result
    assert result['flavors'] == {'1': 'small', '2': 'medium'}
    assert result['suitable_flavors']['1']['ram'] == 2048



@mock.patch("myplugin.content.eduvmstore.view.instances.neutron.network_list_for_tenant")
def test_get_networks_success(mock_list, view_instance):
    n1 = mock.Mock()
    n1.id = 'net1'
    n1.name = 'Public'

    n2 = mock.Mock()
    n2.id = 'net2'
    n2.name = 'Private'

    mock_list.return_value = [n1, n2]

    result = view_instance.get_networks()
    assert result == {'net1': 'Public', 'net2': 'Private'}


@mock.patch("myplugin.content.eduvmstore.view.instances.neutron.network_list_for_tenant", side_effect=Exception("fail"))
def test_get_networks_exception(mock_list, view_instance):
    result = view_instance.get_networks()
    assert result == {}



def test_format_description():
    view = InstancesView()
    text = "   this is   a very long     description with extra   spaces and line\nbreaks  "
    result = view.format_description(text)
    assert "  " not in result
    assert len(result) <= 255



@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template")
def test_extract_accounts_from_form_new(mock_template):
    view = InstancesView()
    mock_template.return_value = {
        'account_attributes': [{'name': 'username'}, {'name': 'password'}]
    }
    view.kwargs = {'image_id': 'img-001'}

    factory = RequestFactory()
    request = factory.post('/')
    post_data = QueryDict('', mutable=True)
    post_data.setlist('username_1', ['user1', 'user2'])
    post_data.setlist('password_1', ['pass1', 'pass2'])
    request.POST = post_data
    view.request = request


    result = view.extract_accounts_from_form_new(view.request, 1)
    assert len(result) == 2
    assert result[0] == {'username': 'user1', 'password': 'pass1'}
    assert result[1] == {'username': 'user2', 'password': 'pass2'}



@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template")
def test_extract_accounts_from_form_instantiation(mock_template):
    view = InstancesView()
    mock_template.return_value = {
        'instantiation_attributes': [{'name': 'hostname'}, {'name': 'domain'}]
    }
    view.kwargs = {'image_id': 'img-001'}

    factory = RequestFactory()
    request = factory.post('/')
    post_data = QueryDict('', mutable=True)
    post_data.setlist('hostname_1_instantiation', ['host1'])
    post_data.setlist('domain_1_instantiation', ['example.com'])
    request.POST = post_data
    view.request = request

    result = view.extract_accounts_from_form_instantiation(view.request, 1)
    assert len(result) == 1
    assert result[0] == {'hostname': 'host1', 'domain': 'example.com'}

@mock.patch("myplugin.content.eduvmstore.view.instances.nova.flavor_list")
def test_get_flavors_malformed_flavor(mock_list, view_instance):
    bad_flavor = mock.Mock()
    del bad_flavor.id
    mock_list.return_value = [bad_flavor]

    result = view_instance.get_flavors({})
    assert result == {}


@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template", return_value={'account_attributes': None})
def test_get_expected_fields_none(mock_template, view_instance):
    view_instance.kwargs = {'image_id': 'img-001'}
    result = view_instance.get_expected_fields()
    assert result == []


@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template", return_value={
    'account_attributes': [{'name': 'username'}, {'name': 'password'}]
})
def test_extract_accounts_from_form_new_inconsistent_fields(mock_template, view_instance):
    factory = RequestFactory()
    request = factory.post('/')
    post_data = QueryDict('', mutable=True)
    post_data.setlist('username_1', ['user1', 'user2'])
    post_data.setlist('password_1', ['pass1'])
    request.POST = post_data
    view_instance.request = request

    with pytest.raises(ValueError, match="Inconsistent account field lengths in form data."):
        view_instance.extract_accounts_from_form_new(request, 1)



@mock.patch("myplugin.content.eduvmstore.view.instances.render", return_value=HttpResponse("ErrorPage"))
@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template", return_value={
    'name': 'test',
    'description': '',
    'image_id': 'img-123',
    'volume_size_gb': 5,
    'ssh_user_requested': False,
    'security_groups': [],
    'account_attributes': [],
    'instantiation_attributes': []
})
def test_post_missing_instance_name(mock_template, mock_render, mock_post_request):
    del mock_post_request.POST["instances_name"]  # Name fehlt
    view = InstancesView()
    view.setup(mock_post_request, image_id="img-123")

    response = view.post(mock_post_request)
    assert response.status_code == 200
    assert b"ErrorPage" in response.content




@mock.patch("myplugin.content.eduvmstore.view.instances.render", return_value=HttpResponse("ErrorPage"))
@mock.patch("myplugin.content.eduvmstore.view.instances.cinder.volume_create", side_effect=Exception("Cinder error"))
@mock.patch("myplugin.content.eduvmstore.view.instances.get_app_template", return_value={
    'name': 'test',
    'description': '',
    'image_id': 'img-123',
    'volume_size_gb': 5,
    'ssh_user_requested': False,
    'security_groups': [],
    'account_attributes': [],
    'instantiation_attributes': []
})
def test_post_volume_creation_error(mock_template, mock_volume_create, mock_render, mock_post_request):
    view = InstancesView()
    view.setup(mock_post_request, image_id="img-123")
    response = view.post(mock_post_request)
    assert b"ErrorPage" in response.content
