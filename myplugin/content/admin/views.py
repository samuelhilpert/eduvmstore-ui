import requests
from django.shortcuts import redirect
from django.contrib import messages
from django.views import generic
from myplugin.content.api_endpoints import API_ENDPOINTS
from openstack_dashboard.api import keystone
from myplugin.content.admin.utils import get_token_id




class UpdateRolesView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to update a user's role via the external API.
        """
        user_id = request.POST.get("user_id")
        new_role_id = request.POST.get("new_role_id")
        token_id = get_token_id(request)


        if not user_id or not new_role_id:
            messages.error(request, "User ID and Role ID are required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API-Call
            api_url = f"{API_ENDPOINTS['user_list']}{user_id}/"

            payload = {"role_id": new_role_id}
            headers = {"X-Auth-Token": token_id}

            # API-PATCH-Call
            response = requests.patch(api_url, json=payload, headers=headers,timeout=10)

            if response.status_code == 200:
                messages.success(request, f"Role for user {user_id} updated successfully to {new_role_id}.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to update role: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')


class ApproveTemplateView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to approve a template via the Backend.
        """
        template_id = request.POST.get("template_id")
        token_id = get_token_id(request)


        if not template_id:
            messages.error(request, "App Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API-Call
            api_url = f"{API_ENDPOINTS['app_templates']}{template_id}/approve/"

            headers = {"X-Auth-Token": token_id}

            # API-PATCH-Call
            response = requests.patch(api_url, headers=headers,timeout=10)

            if response.status_code == 200:
                messages.success(request, f"{template_id} confirmed. This app template is now public.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to approve app template: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')


class RejectTemplateView(generic.View):

    """
    Handle POST requests to reject a template via the Backend.
    """
    def post(self, request, *args, **kwargs):

        template_id = request.POST.get("template_id")
        token_id = get_token_id(request)


        if not template_id:
            messages.error(request, "App Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API-Call
            api_url = f"{API_ENDPOINTS['app_templates']}{template_id}/reject/"

            headers = {"X-Auth-Token": token_id}

            # API-PATCH-Call
            response = requests.patch(api_url, headers=headers,timeout=10)

            if response.status_code == 200:
                messages.success(request, f"{template_id} rejected. This app template remains private.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to reject app template: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')

class DeleteTemplateView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete a template via the external API.
        """
        template_id = request.POST.get("template_id")
        token_id = get_token_id(request)

        if not template_id:
            messages.error(request, "Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API call
            api_url = f"{API_ENDPOINTS['app_templates']}{template_id}/"

            headers = {"X-Auth-Token": token_id}

            # API DELETE call
            response = requests.delete(api_url, headers=headers,timeout=10)

            if response.status_code == 204:
                messages.success(request, f"Template {template_id} deleted successfully.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to delete template: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')

class DeleteUserView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete a template via the external API.
        """
        user_id = request.POST.get("user_id")
        token_id = get_token_id(request)

        if not user_id:
            messages.error(request, "Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API call
            api_url = f"{API_ENDPOINTS['user_list']}{user_id}/"

            headers = {"X-Auth-Token": token_id}

            # API DELETE call
            response = requests.delete(api_url, headers=headers,timeout=10)

            if response.status_code == 204:
                messages.success(request, f"User {user_id} deleted successfully.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to delete user: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')

class CreateRoleView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete a template via the external API.
        """
        new_role_name = request.POST.get("new_role_name")
        access_level = request.POST.get("access_level")
        token_id = get_token_id(request)

        if not new_role_name:
            messages.error(request, "Role Name is required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API call
            api_url = f"{API_ENDPOINTS['roles_list']}/"

            headers = {"X-Auth-Token": token_id}

            payload = {
                "name": new_role_name,
                "access_level": access_level
            }


            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                created_role = response.json()
                role_id = created_role.get("id")
                messages.success(request, f"Role '{new_role_name}' created successfully with ID {role_id}.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to create role: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:admin:index')