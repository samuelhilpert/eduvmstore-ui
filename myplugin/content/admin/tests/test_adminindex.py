import pytest
from unittest import mock
from django.test import RequestFactory
from myplugin.content.admin.view.index import IndexView


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def fake_user():
    user = mock.MagicMock()
    user.token.id = 'test-token'
    user.id = 'user-123'
    user.username = 'admin'
    user.is_superuser = True
    return user


@pytest.fixture
def view_instance(fake_user):
    request = RequestFactory().get('/')
    request.user = fake_user
    view = IndexView()
    view.setup(request)
    return view


@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 999}})
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[{"id": "user-123"}])
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "EduVMStoreAdmin", "access_level": 999}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[{"creator_id": "user-123"}])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[{"name": "template1"}])
def test_get_context_data(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance
):
    context = view_instance.get_context_data()
    assert context["username"] == "admin"
    assert context["auth_token"] == "test-token"
    assert context["admin"] is True
    assert context["show_content"] is True
    assert context["detailed_users"][0]["username"] == "admin_user"
    assert "approvable_app_templates" in context
    assert "app_templates" in context
    assert "roles" in context
    assert "users" in context

@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 10}})
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[{"id": "user-123"}])
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "SomeOtherRole", "access_level": 5}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[])
def test_get_context_data_no_admin_access(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance
):
    context = view_instance.get_context_data()
    assert context["show_content"] is False

@mock.patch("myplugin.content.admin.view.index.get_user_details", side_effect=Exception("API down"))
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "EduVMStoreAdmin", "access_level": 999}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[])
def test_context_data_user_details_exception(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance):
    context = view_instance.get_context_data()
    assert context["show_content"] is False


@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 999}})
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_roles", side_effect=Exception("Role error"))
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[])
def test_context_data_get_roles_exception(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance):
    context = view_instance.get_context_data()
    assert context["roles"] == []
    assert context["show_content"] is False


@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 999}})
@mock.patch("myplugin.content.admin.view.index.get_users", side_effect=Exception("User list failed"))
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "EduVMStoreAdmin", "access_level": 999}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[])
def test_context_data_get_users_exception(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance):
    context = view_instance.get_context_data()
    assert context["users"] == []
    assert context["detailed_users"] == []


@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 999}})
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "EduVMStoreAdmin", "access_level": 999}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", side_effect=Exception("approval API down"))
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", return_value=[])
def test_context_data_approvables_exception(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance):
    context = view_instance.get_context_data()
    assert context["approvable_app_templates"] == []

@mock.patch("myplugin.content.admin.view.index.get_user_details", return_value={"role": {"access_level": 999}})
@mock.patch("myplugin.content.admin.view.index.get_users", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_roles", return_value=[{"name": "EduVMStoreAdmin", "access_level": 999}])
@mock.patch("myplugin.content.admin.view.index.get_app_templates_to_approve", return_value=[])
@mock.patch("myplugin.content.admin.view.index.get_username_from_id", return_value="admin_user")
@mock.patch("myplugin.content.admin.view.index.get_app_templates", side_effect=Exception("template failure"))
def test_context_data_app_templates_exception(
        mock_templates, mock_username, mock_approve, mock_roles, mock_users, mock_user_details, view_instance):
    context = view_instance.get_context_data()
    assert context["app_templates"] == []

