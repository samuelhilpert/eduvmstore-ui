import requests
import socket
import logging
from django.shortcuts import redirect
from django.contrib import messages
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

def change_user_role(request):
    """
    Ändert die Rolle eines Benutzers über einen API-PATCH-Aufruf.
    """
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        new_role_id = request.POST.get(f"new_role_{user_id}")

        if user_id and new_role_id:
            try:
                # Basis-URL und Endpunkt konfigurieren
                api_url = f"{API_ENDPOINTS['user_list']}{user_id}"  #

                # Header und Daten vorbereiten
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {request.user.token.id}",  # Beispiel-Token
                }
                payload = {"role": new_role_id}

                # PATCH-Request ausführen
                response = requests.patch(api_url, json=payload, headers=headers)

                if response.status_code == 200:
                    messages.success(request, f"Role for user {user_id} updated successfully via API.")
                else:
                    # API-Fehlermeldung extrahieren
                    error_message = response.json().get("error", "Unknown error occurred.")
                    messages.error(request, f"Failed to update role via API: {error_message}")
            except requests.RequestException as e:
                messages.error(request, f"Error during API call: {str(e)}")
        else:
            messages.error(request, "User ID or new role not provided.")

    return redirect("index")  # Passe den View-Namen an

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











