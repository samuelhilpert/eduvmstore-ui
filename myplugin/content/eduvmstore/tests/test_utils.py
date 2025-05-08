import pytest
from unittest import mock
import requests
from django.test import RequestFactory
from myplugin.content.eduvmstore import utils


def test_get_token_id():
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    assert utils.get_token_id(request) == "test-token"


@mock.patch("myplugin.content.eduvmstore.utils.requests.get")
def test_search_app_templates_success(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    request.GET.get.return_value = "test"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"id": 1}]
    result = utils.search_app_templates(request)
    assert result == [{"id": 1}]


@mock.patch("myplugin.content.eduvmstore.utils.requests.get")
def test_fetch_favorite_app_templates_success(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"id": "fav1"}]
    result = utils.fetch_favorite_app_templates(request)
    assert result == [{"id": "fav1"}]


@mock.patch("myplugin.content.eduvmstore.utils.glance.image_list_detailed")
def test_get_images_data_success(mock_list):
    request = mock.MagicMock()
    mock_img = mock.MagicMock(id="img1")
    mock_list.return_value = ([mock_img], False, False)
    result = utils.get_images_data(request)
    assert result == {"img1": mock_img}


@mock.patch("myplugin.content.eduvmstore.utils.glance.image_get")
def test_get_image_data_success(mock_get):
    request = mock.MagicMock()
    image = mock.MagicMock(visibility="public", owner="admin")
    mock_get.return_value = image
    result = utils.get_image_data(request, "img1")
    assert result == {"visibility": "public", "owner": "admin"}


@mock.patch("myplugin.content.eduvmstore.utils.requests.get")
def test_get_app_template_success(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"id": "template1"}
    result = utils.get_app_template(request, "template1")
    assert result == {"id": "template1"}


def test_generate_indented_content():
    content = "line1\nline2"
    result = utils.generate_indented_content(content, indent_level=4)
    assert result == "    line1\n    line2"


def test_generate_cloud_config_all_fields():
    accounts = [{"username": "test", "password": "pass"}]
    inst = [{"hostname": "host1"}]
    script = "#!/bin/bash echo hi"
    result = utils.generate_cloud_config(accounts, script, inst)
    assert "#cloud-config" in result
    assert "write_files:" in result
    assert script in result


def test_generate_pdf_bytes():
    result = utils.generate_pdf(
        accounts=[{"username": "user1"}],
        name="test-inst",
        app_template="Ubuntu",
        created="2024-12-01",
        instantiations=[{"hostname": "h1"}],
        ip_address="1.2.3.4"
    )
    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")


def test_generate_ssh_instructions_pdf():
    result = utils.generate_ssh_instructions_pdf(
        [{"name": "vm1", "ip": "1.2.3.4", "key": "key.pem"}]
    )
    assert isinstance(result, bytes)
    assert result.startswith(b"%PDF")


@mock.patch("myplugin.content.eduvmstore.utils.requests.get", side_effect=requests.RequestException("error"))
def test_search_app_templates_exception(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    request.GET.get.return_value = "abc"
    result = utils.search_app_templates(request)
    assert result == []


@mock.patch("myplugin.content.eduvmstore.utils.requests.get", side_effect=requests.RequestException("fail"))
def test_fetch_favorite_app_templates_exception(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    result = utils.fetch_favorite_app_templates(request)
    assert result == []


@mock.patch("myplugin.content.eduvmstore.utils.glance.image_get", side_effect=Exception("not found"))
def test_get_image_data_exception(mock_get):
    request = mock.MagicMock()
    result = utils.get_image_data(request, "img1")
    assert result == {}


@mock.patch("myplugin.content.eduvmstore.utils.requests.get",
            side_effect=requests.RequestException("API down"))
def test_get_app_template_exception(mock_get):
    request = mock.MagicMock()
    request.user.token.id = "test-token"
    result = utils.get_app_template(request, "template1")
    assert result == {}


def test_generate_cloud_config_script_only():
    script = "#!/bin/bash\necho hello"
    result = utils.generate_cloud_config([], script, [])
    assert result.startswith("#cloud-config")
    assert script in result
