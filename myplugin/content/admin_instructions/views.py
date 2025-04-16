from http.client import responses

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext_lazy as _

from myplugin.content.api_endpoints import API_ENDPOINTS

import requests
import logging
import sys

from django.views.decorators.csrf import csrf_exempt

def get_token_id(request):
    """
    Retrieves the token ID from the request object.
    """
    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id

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



class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/admin_instructions/index.html'
    page_title = _("Admin Instructions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_id = self.request.user.id
        user_details = get_user_details(self.request, user_id)
        role_level = user_details.get('role', {}).get('access_level', 1)

        roles_data = get_roles(self.request)
        admin_access_level = sys.maxsize
        for item in roles_data:
            if item["name"] == "EduVMStoreAdmin":
                admin_access_level = item["access_level"]
                break

        context['show_content'] = False

        # Check if the user is an admin
        if role_level >= admin_access_level:
            context['show_content'] = True
        else:
            context['show_content'] = False

        context['page_title'] = self.page_title
        return context