import requests
import socket
import logging
from django.views import generic
from myplugin.content.api_endpoints import API_ENDPOINTS

# Retrieve the host IP address
def get_host_ip():
    """
        Retrieve the IP address of the host.

        :return: The IP address of the host.
        :rtype: str
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        raise RuntimeError("Failed to retrieve host IP address") from e
    finally:
        s.close()
    return ip

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
    url = f"{API_ENDPOINTS['user_list']}{user_id}"  #

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch user details for user_id %s: %s", user_id, e)
        return {}

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

        user_data = get_users(self.request)
        context['users'] = user_data

        roles_data = get_roles(self.request)
        context['roles'] = roles_data

        detailed_users = []
        for user in user_data:
            user_id = user.get('id')  # Assuming the API response includes an 'id' field
            if user_id:
                user_details = get_user_details(self.request, user_id)
                detailed_users.append(user_details)

        context['detailed_users'] = detailed_users

        # Add user details and admin status to the context
        context['username'] = userdev.username
        context['auth_token'] = token_id
        context['admin'] = userdev.is_superuser
        context['show_content'] = False

        # Check if the user is an admin and set the content visibility accordingly
        if userdev.is_superuser:
            context['show_content'] = True
        else:
            context['show_content'] = False


        return context











