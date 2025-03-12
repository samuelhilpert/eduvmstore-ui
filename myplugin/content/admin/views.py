import requests
import socket
import logging
from django.shortcuts import redirect
from django.contrib import messages
from django.views import generic
from myplugin.content.api_endpoints import API_ENDPOINTS


def get_token_id(request):
    """
    Retrieves the token ID from the request object.
    """
    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id

def get_users(request):
    """
    Fetches app templates from the external API using a provided token ID.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['user_list'],
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch users: %s", e)
        return []

def get_roles(request):
    """
    Fetches app templates from the external API using a provided token ID.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['roles_list'],
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch roles: %s", e)
        return []

def get_user_details(request, user_id):
    """
    Fetches detailed user information for a given user_id using the external API.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}
    url = f"{API_ENDPOINTS['user_list']}{user_id}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch user details for user_id %s: %s", user_id, e)
        return {}

def get_app_templates_to_approve(request):
    """
    Fetches app templates to approve from the external API using a provided token ID.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['get_to_approve'],
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch app templates to approve: %s", e)
        return []

def get_app_templates(request):
    """
    Fetches app templates from the external API using a provided token ID.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['app_templates'],
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch app templates: %s", e)
        return []


class IndexView(generic.TemplateView):
    """
        View for displaying the admin index page with user details and admin status.
    """
    template_name = 'eduvmstore_dashboard/admin/index.html'

    def get_context_data(self, **kwargs):
        """
            Add user details, authentication token, and admin status to the context.

            :param kwargs: Additional context parameters.
            :return: Context dictionary with user-specific details and content visibility.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        userdev = self.request.user
        token_id = None

        # Check if the user has a token attribute and retrieve its ID
        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        user_id = self.request.user.id
        user_details = get_user_details(self.request, user_id)
        role_level = user_details['role']['access_level']
        user_data = get_users(self.request)
        context['users'] = user_data

        roles_data = get_roles(self.request)
        context['roles'] = roles_data

        approvable_app_templates = get_app_templates_to_approve(self.request)
        context['approvable_app_templates'] = approvable_app_templates

        app_templates = get_app_templates(self.request)
        context['app_templates'] = app_templates

        detailed_users = []
        for user in user_data:
            user_id = user.get('id')
            if user_id:
                user_details = get_user_details(self.request, user_id)
                detailed_users.append(user_details)

        context['detailed_users'] = detailed_users

        # Add user details and admin status to the context
        context['username'] = userdev.username
        context['auth_token'] = token_id
        context['admin'] = userdev.is_superuser
        context['show_content'] = False

        # Check if the user is an admin, if its equal or greater than 6000 it is an admin
        if role_level >= 6000:
            context['show_content'] = True
        else:
            context['show_content'] = False



        return context


class UpdateRolesView(generic.View):
    """
    Handle POST requests to update a user's role via the Backend.
    """
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
    """
    Handle POST requests to update a user's role via the Backend.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to update a user's role via the external API.
        """
        template_id = request.POST.get("template_id")
        token_id = get_token_id(request)


        if not template_id:
            messages.error(request, "Template ID are required.")
            return redirect('horizon:eduvmstore_dashboard:admin:index')

        try:
            # Prepare API-Call
            api_url = f"{API_ENDPOINTS['app_templates']}{template_id}/approved/"

            headers = {"X-Auth-Token": token_id}

            # API-PATCH-Call
            response = requests.patch(api_url, headers=headers,timeout=10)

            if response.status_code == 200:
                messages.success(request, f"{template_id} confirmed. This template is now public.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to update role: {error_message}")
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