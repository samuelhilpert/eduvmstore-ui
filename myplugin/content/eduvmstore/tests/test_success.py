import pytest
from unittest import mock
from django.test import RequestFactory
from django.http import HttpResponse, QueryDict
from myplugin.content.eduvmstore.view.success import InstanceSuccessView


@pytest.fixture
def view_with_session():
    view = InstanceSuccessView()
    request = RequestFactory().get('/')
    request.session = {
        "num_instances": 2,
        "separate_keys": True,
        "ssh_user_requested": True,
        "keypair_name_1": "key1",
        "keypair_name_2": "key2",
        "names_1": "inst1",
        "names_2": "inst2",
        "ip_addresses_1": "10.0.0.1",
        "ip_addresses_2": "10.0.0.2",
    }
    view.request = request
    return view


def test_get_context_data(view_with_session):
    context = view_with_session.get_context_data()
    assert context['ssh_user_requested'] is True
    assert context['page_title'] == view_with_session.page_title
    assert len(context['instances']) == 2
    assert context['instances'][0]['name'] == 'inst1'
    assert context['instances'][1]['ip'] == '10.0.0.2'


@mock.patch("myplugin.content.eduvmstore.view.success.generate_pdf", return_value=b"%PDF-1.4 dummy")
@mock.patch("myplugin.content.eduvmstore.view.success.generate_ssh_instructions_pdf", return_value=b"%PDF-1.4 ssh")
def test_post_creates_zip(mock_ssh_pdf, mock_account_pdf):
    request = RequestFactory().post('/')
    request.session = {
        "num_instances": 1,
        "separate_keys": False,
        "ssh_user_requested": True,
        "keypair_name": "sharedkey",
        "private_key": "PRIVATEKEY",
        "names_1": "demo-instance",
        "ip_addresses_1": "192.168.1.5",
        "accounts_1": [{"username": "user1"}],
        "instantiations_1": [{"hostname": "demo"}],
        "app_template": "UbuntuTemplate",
        "created": "2024-12-01",
        "base_name": "demo"
    }

    view = InstanceSuccessView()
    view.request = request
    response = view.post(request)

    assert isinstance(response, HttpResponse)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"
    assert "attachment" in response["Content-Disposition"]

@mock.patch("myplugin.content.eduvmstore.view.success.generate_pdf")
@mock.patch("myplugin.content.eduvmstore.view.success.generate_ssh_instructions_pdf")
def test_post_without_accounts_or_ssh(mock_ssh_pdf, mock_account_pdf):
    request = RequestFactory().post('/')
    request.session = {
        "num_instances": 1,
        "separate_keys": False,
        "ssh_user_requested": False,
        "keypair_name": "sharedkey",
        "private_key": "PRIVATEKEY",
        "names_1": "demo-instance",
        "ip_addresses_1": "192.168.1.5",
        "app_template": "UbuntuTemplate",
        "created": "2024-12-01",
        "base_name": "demo"
        # Kein accounts_1, kein instantiations_1
    }

    view = InstanceSuccessView()
    view.request = request
    response = view.post(request)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/zip"

    # Sicherstellen, dass KEINE PDFs generiert wurden
    mock_account_pdf.assert_not_called()
    mock_ssh_pdf.assert_not_called()
