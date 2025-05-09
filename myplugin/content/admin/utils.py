# in this file, we define utility functions for the admin panel
from openstack_dashboard.api import keystone
import requests
import logging
from myplugin.content.api_endpoints import API_ENDPOINTS


def get_username_from_id(request, user_id):
    """
    Retrieves the username for a given user ID using the Keystone API.

    This function attempts to fetch the user details from the Keystone API
    and returns the user's name. If an exception occurs during the process,
    it returns the provided user ID as a fallback.

    Args:
        request: The HTTP request object containing user authentication details.
        user_id (str): The ID of the user whose name is to be retrieved.

    Returns:
        str: The username if successfully retrieved, otherwise the user ID.
    """
    try:
        user = keystone.user_get(request, user_id)
        return user.name
    except Exception:
        return user_id


def get_token_id(request):
    """
    Retrieves the token ID from the request object.

    This function accesses the `user` attribute of the request object and
    retrieves the token ID if it exists. If the `user` or `token` attribute
    is not present, it returns `None`.

    Args:
        request: The HTTP request object containing user authentication details.

    Returns:
        str or None: The token ID if available, otherwise `None`.
    """
    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id


def get_users(request):
    """
    Fetches a list of users from the external API using the provided token ID.

    This function retrieves the token ID from the request object and uses it
    to authenticate a GET request to the 'user_list' endpoint. If the request
    is successful, it returns the JSON response containing the list of users.
    In case of an error, it logs the error and returns an empty list.

    Args:
        request: The HTTP request object containing user authentication details.

    Returns:
        list: A list of users retrieved from the external API, or an empty list
        if the request fails.
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
    Fetches a list of roles from the external API using the provided token ID.

    This function retrieves the token ID from the request object and uses it
    to authenticate a GET request to the 'roles_list' endpoint. If the request
    is successful, it returns the JSON response containing the list of roles.
    In case of an error, it logs the error and returns an empty list.

    Args:
        request: The HTTP request object containing user authentication details.

    Returns:
        list: A list of roles retrieved from the external API, or an empty list
        if the request fails.
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
    Fetches detailed user information for a given user ID using the external API.

    This function retrieves the token ID from the request object and uses it
    to authenticate a GET request to the external API's user details endpoint.
    If the request is successful, it returns the JSON response containing the
    user's details. In case of an error, it logs the error and returns an empty
    dictionary.

    Args:
        request: The HTTP request object containing user authentication details.
        user_id (str): The ID of the user whose details are to be retrieved.

    Returns:
        dict: A dictionary containing the user's details if the request is
        successful, or an empty dictionary if the request fails.
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
    Fetches a list of app templates pending approval from the external API.

    This function retrieves the token ID from the request object and uses it
    to authenticate a GET request to the 'get_to_approve' endpoint. If the
    request is successful, it returns the JSON response containing the list
    of app templates. In case of an error, it logs the error and returns an
    empty list.

    Args:
        request: The HTTP request object containing user authentication details.

    Returns:
        list: A list of app templates pending approval, or an empty list if
        the request fails.
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
    Fetches a list of app templates from the external API using the provided token ID.

    This function retrieves the token ID from the request object and uses it
    to authenticate a GET request to the 'app_templates' endpoint. If the
    request is successful, it returns the JSON response containing the list
    of app templates. In case of an error, it logs the error and returns an
    empty list.

    Args:
        request: The HTTP request object containing user authentication details.

    Returns:
        list: A list of app templates retrieved from the external API, or an
        empty list if the request fails.
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
