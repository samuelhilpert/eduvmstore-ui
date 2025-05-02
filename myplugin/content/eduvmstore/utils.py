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

def get_app_template(request, template_id):
    """
    Fetch a specific AppTemplate from the external database using token authentication.

    :param request: Django request object.
    :param template_id: The ID of the AppTemplate to retrieve.
    :return: JSON response of AppTemplate details if successful, otherwise an empty dict.
    """
    token_id = get_token_id(request)
    headers = {"X-Auth-Token": token_id}
    try:
        response = requests.get(
            API_ENDPOINTS['app_template_detail'].format(template_id=template_id),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Unable to retrieve app template details: %s", e)
        return {}

def generate_pdf(accounts, name, app_template, created, instantiations, ip_address):
    """
    Generate a well-formatted PDF document containing user account information in a table format.

    :param accounts: A list of dictionaries, where each dictionary contains user account details.
    :type accounts: list
    :param name: The name of the created instance.
    :type name: str
    :return: PDF-Datei als Bytes (nicht als HttpResponse!)
    :rtype: bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(f"<b>{name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    subtitle = Paragraph(
        f"Instantiation Attributes for the created instance {name} from the EduVMStore. "
        f"This instance was created with the app template {app_template} on {created}.",
        styles['Normal']

    )
    elements.append(subtitle)
    if ip_address:
        ip = Paragraph(f"IP Address: {ip_address}", styles['Normal'])
        elements.append(ip)
    elements.append(Spacer(1, 0.2 * inch))

    if accounts:
        elements.append(Paragraph("<b>Account Attributes</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        all_keys = list(accounts[0].keys())
        table_data = [all_keys]
        for account in accounts:
            row_values = [account.get(key, "N/A") for key in all_keys]
            table_data.append(row_values)
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2 * inch))


    if instantiations:
        elements.append(Paragraph("<b>Instantiation Attributes</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))

        keys = list(instantiations[0].keys())
        table_data_instantiation = []

        header_row = ["Attributes"] + ["Values"]
        table_data_instantiation.append(header_row)

        for key in keys:
            row = [key]
            for inst in instantiations:
                row.append(inst.get(key, "N/A"))
            table_data_instantiation.append(row)

        table_instantiation = Table(table_data_instantiation, repeatRows=1)
        table_instantiation.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_instantiation)


    doc.build(elements)
    buffer.seek(0)

    return buffer.getvalue()

def generate_ssh_instructions_pdf(instances):
    """
    Generate a PDF containing SSH copy instructions for the user keys.

    :param instances: A list of instance dictionaries with 'name', 'ip', and 'key'.
    :type instances: list
    :return: PDF content as bytes.
    :rtype: bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph("<b>SSH Instructions for Downloading User Keys</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))
    subtitle = Paragraph(
        f"These instructions will help you to download the private ssh user keys from the instances."
        f" Please use the following commands to copy the keys from the instances to your local machine.",
        styles['Normal']

    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2 * inch))

    for idx, instance in enumerate(instances, start=1):
        name = instance.get('name', 'Unknown')
        ip = instance.get('ip', 'Unknown')
        key = instance.get('key', 'Unknown')
        command = f"scp -i {key} -r ubuntu@{ip}:/home/ubuntu/user_keys/ ."

        elements.append(Paragraph(f"<b>{name}</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(command, styles['Code']))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    buffer.seek(0)

    return buffer.getvalue()



def generate_cloud_config(accounts, backend_script, instantiations):
    """
    Generate a cloud-config file for user account creation and backend script execution.

    :param accounts: A list of dictionaries with user account details.
    :param backend_script: Backend script to be included in the cloud-config.
    :param instantiations: A list of dictionaries with instantiation data.
    :return: A string representing the complete cloud-config file.
    """

    users_content = ""
    instantiations_content = ""

    if accounts:
        sorted_keys = list(accounts[0].keys())
        users_content = "\n".join(
            [":".join([account.get(key, "N/A") for key in sorted_keys]) for account in accounts]
        )

    if instantiations:
        sorted_keys_instantiation = list(instantiations[0].keys())
        instantiations_content = "\n".join(
            [":".join([inst.get(key, "N/A") for key in sorted_keys_instantiation])
             for inst in instantiations]
        )

    write_files_block = ""

    if users_content:
        write_files_block += f"""
  - path: /etc/users.txt
    content: |
{generate_indented_content(users_content, indent_level=6)}
    permissions: '0644'
    owner: root:root
"""

    if instantiations_content:
        write_files_block += f"""
  - path: /etc/attributes.txt
    content: |
{generate_indented_content(instantiations_content, indent_level=6)}
    permissions: '0644'
    owner: root:root
"""

    cloud_config = "#cloud-config\n"
    if write_files_block:
        cloud_config += f"write_files:{write_files_block}"

    if backend_script:
        cloud_config += f"\n\n{backend_script}"

    return cloud_config



def generate_indented_content(content, indent_level=6):
    """
    Indent each line of the given content by a specified number of spaces.

    This function takes a multi-line string and indents each line by a specified number of spaces.
    It is useful for formatting content that needs to be indented consistently.

    :param content: The multi-line string to be indented.
    :type content: str
    :param indent_level: The number of spaces to indent each line.
    :type indent_level: int
    :return: The indented multi-line string.
    :rtype: str
    """

    indent = " " * indent_level
    return "\n".join([indent + line for line in content.split("\n")])