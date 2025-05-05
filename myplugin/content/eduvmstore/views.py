
import requests
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from horizon import tabs, exceptions
from openstack_dashboard.api import glance, nova, cinder, keystone, neutron
from django.views import generic
from myplugin.content.api_endpoints import API_ENDPOINTS
from django.http import HttpResponse

from django.views import View

from myplugin.content.eduvmstore.utils import get_token_id


#This module contains helper views that do not directly render content for the EduVMStore dashboard.

#It includes:
# - POST handlers triggered via forms (e.g., favoriting or deleting AppTemplates)
# - Utility functions such as AppTemplate name validation
# - No content-related views — those are located in `myplugin.content.eduvmstore.view`



def validate_name(request):
    """
    Validate the uniqueness of a name by checking for a collision via the EduVMStore
    Backend API

    This function handles POST requests to validate a name by sending it to the
    EduVMStore Backend API and checking for any name collision.
    It uses the token ID from the request for authentication.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: JsonResponse indicating whether the name is valid or an error message
            if the request method is invalid.
    :rtype: JsonResponse
    """
    if request.method == "POST":
        try:
            # Read JSON-Body
            body = json.loads(request.body)
            name = body.get('name', '').strip()

            # Retrieve Token-ID
            token_id = get_token_id(request)
            headers = {"X-Auth-Token": token_id}

            # API-Calls to Backend
            url = f"{API_ENDPOINTS['check_name']}{name}/collision"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Process Response
            data = response.json()
            is_valid = not data.get('collision', True)

        except (requests.RequestException, ValueError, json.JSONDecodeError):
            is_valid = False

        return JsonResponse({'valid': is_valid, 'reason': data.get('reason', 'Name already taken')})


    return JsonResponse({'error': 'Invalid request method'}, status=400)


class GetFavoriteAppTemplateView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to mark an AppTemplate as a favorite via the external API.

        This method retrieves the AppTemplate ID and name from the POST request,
        constructs the API URL and payload, and sends a POST request to the external API.
        It handles the response and displays appropriate success or error messages.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: HTTP response redirecting to the index page.
        :rtype: HttpResponse
        """

        favorite_app_template_id = request.POST.get("template_id")
        favorite_name = request.POST.get("template_name")
        token_id = get_token_id(request)

        if not favorite_app_template_id:
            messages.error(request, "App Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        try:
            api_url = f"{API_ENDPOINTS['to_be_favorite']}"

            headers = {"X-Auth-Token": token_id}

            payload = {
                "app_template_id": favorite_app_template_id
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 201:
                messages.success(request, f"App Template '{favorite_name}' is now a favorite.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to favorite app template: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

class DeleteFavoriteAppTemplateView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to delete a favorite AppTemplate via the external API.

        This method retrieves the AppTemplate ID and name from the POST request,
        constructs the API URL and payload, and sends a DELETE request to the external API.
        It handles the response and displays appropriate success or error messages.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: HTTP response redirecting to the index page.
        :rtype: HttpResponse
        """

        favorite_app_template_id = request.POST.get("template_id")
        favorite_name = request.POST.get("template_name")
        token_id = get_token_id(request)

        if not favorite_app_template_id:
            messages.error(request, "App Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        try:
            api_url = f"{API_ENDPOINTS['delete_favorite']}"

            headers = {"X-Auth-Token": token_id}

            payload = {
                "app_template_id": favorite_app_template_id
            }

            response = requests.delete(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 204:
                messages.success(request, f"'{favorite_name}' is not a favorite now.")
            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to delete  as a favorite: {error_message}")
        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')


class DeleteTemplateView(View):
    """Handles AppTemplate deletion.
       Deletion is allowed only if the image owner (from Glance) matches the user ID returned from Keystone.
       After deletion, it also attempts to remove the template from favorites.
    """

    def post(self, request, template_id):
        token_id = get_token_id(request)
        template_name = request.POST.get("template_name")

        if not token_id:
            messages.error(request, "Authentication token not found.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        if not template_id:
            messages.error(request, "App Template ID is required.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        headers = {"X-Auth-Token": token_id}

        detail_api_url = API_ENDPOINTS['app_template_detail'].format(template_id=template_id)
        try:
            detail_response = requests.get(detail_api_url, headers=headers, timeout=10)
            if detail_response.status_code != 200:
                messages.error(request, "Failed to fetch template details.")
                return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')
            template_detail = detail_response.json()
        except requests.RequestException as e:
            messages.error(request, f"Error fetching template details: {str(e)}")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        creator_id = template_detail.get('creator_id')

        user_id = self.request.user.token.user['id']
        if not user_id:
            messages.error(request, "Could not verify logged-in user with Keystone.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        if creator_id.replace('-', '') != user_id.replace('-', ''):

            messages.error(request, "You are not authorized to delete this template.")
            return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')

        try:
            api_url = API_ENDPOINTS['app_template_delete'].format(template_id=template_id)
            response = requests.delete(api_url, headers=headers, timeout=10)

            if response.status_code == 204:
                messages.success(request, f"'{template_name}' was successfully deleted.")

                try:
                    favorite_api_url = API_ENDPOINTS['delete_favorite']
                    payload = {"app_template_id": template_id}
                    fav_response = requests.delete(favorite_api_url, json=payload, headers=headers,
                                                   timeout=10)
                    if fav_response.status_code not in [204, 404]:
                        error_message = fav_response.json().get("error", "Unknown error occurred.")
                        messages.warning(
                            request,
                            f"'{template_name}' deleted, but still a favorite: {error_message}")
                except requests.RequestException:
                    pass

            else:
                error_message = response.json().get("error", "Unknown error occurred.")
                messages.error(request, f"Failed to delete '{template_name}': {error_message}")

        except requests.RequestException as e:
            messages.error(request, f"Error during API call: {str(e)}")

        return redirect('horizon:eduvmstore_dashboard:eduvmstore:index')