import requests
import socket
import logging
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from horizon import tabs, exceptions
from openstack_dashboard import api
from openstack_dashboard.api import glance, nova, cinder, keystone, neutron
from django.views import generic
from django.utils.translation import gettext_lazy as _
from myplugin.content.api_endpoints import API_ENDPOINTS
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from myplugin.content.eduvmstore.presets import preset_examples

import io
import zipfile
from io import BytesIO
import time

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views import View
import base64
import re

def get_token_id(request):
    """
    Retrieve the token ID from the request object.

    This function extracts the token ID from the user attribute of the request object.
    If the user or token attribute is not present, it returns None.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: The token ID if available, otherwise None.
    :rtype: str or None
    """

    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id

def search_app_templates(request) -> list:
    """
    Search for AppTemplates via the backend API using a provided token ID.

    This function retrieves the token ID from the request, constructs the headers,
    and makes a GET request to the EduVMStore Backend API to search for AppTemplates.
    If the request is successful, it returns the JSON response of AppTemplates.
    In case of an error, it logs the error and returns an empty list.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: A list of AppTemplates in JSON format or an empty list if the request fails.
    :rtype: list
    """

    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    search = request.GET.get('search', '')

    try:
        response = requests.get(f"{API_ENDPOINTS['app_templates']}?search={search}",
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to search app templates: %s", e)
        return []

def fetch_favorite_app_templates(request):
    """
    Fetches favorite AppTemplates from the external API using a provided token ID.

    This function retrieves the token ID from the request, constructs the headers,
    and makes a GET request to the external API to fetch favorite AppTemplates.
    If the request is successful, it returns the JSON response. In case of an error,
    it logs the error and returns an empty list.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: A list of favorite AppTemplates in JSON format or an empty list if the request fails.
    :rtype: list
    """

    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['favorite'],
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch favorite app templates: %s", e)
        return []


def get_images_data(request):
    """
        Fetch alles images from the Glance API using Horizon API.
        :return: Dictionary of images indexed by image IDs.
        :rtype: dict
    """
    try:
        filters = {}
        images, has_more_data, has_prev_data = glance.image_list_detailed(
            request, filters=filters,  paginate=True
        )

        return {image.id: image for image in images}
    except Exception as e:
        logging.error(f"Unable to retrieve images: {e}")
        return {}


def get_image_data(request, image_id):
    """
    Fetch image details from Glance based on the image_id.

    :param request: Django request object.
    :param image_id: ID of the image to retrieve.
    :return: Dictionary with visibility and owner details of the image.
    """
    try:
        image = glance.image_get(request, image_id)
        return {'visibility': image.visibility, 'owner': image.owner}
    except Exception as e:
        exceptions.handle(request, _('Unable to retrieve image details: %s') % str(e))
        return {}