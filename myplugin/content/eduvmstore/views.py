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
from openstack_dashboard.api import glance, nova, cinder, keystone
from openstack_dashboard.api import neutron
from django.views import generic
from myplugin.content.eduvmstore.forms import AppTemplateForm, InstanceForm
from django.utils.translation import gettext_lazy as _
from myplugin.content.api_endpoints import API_ENDPOINTS
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import zipfile
from io import BytesIO
import time

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.views import View
import base64
import re

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_host_ip():
    """
        Retrieve the host's IP address by connecting to an external server.
        :return: IP address of the host machine.
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
    Retrieve the token ID from the request object.

    This function extracts the token ID from the user attribute of the request object.
    If the user or token attribute is not present, it returns None.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: The token ID if available, otherwise None.
    :rtype: str or None
    """

    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id


def fetch_app_templates(request):
    """
    Fetches app templates from the external API using a provided token ID.

    This function retrieves the token ID from the request, constructs the headers,
    and makes a GET request to the external API to fetch app templates. If the request
    is successful, it returns the JSON response. In case of an error, it logs the error
    and returns an empty list.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: A list of app templates in JSON format or an empty list if the request fails.
    :rtype: list
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

def search_app_templates(request) -> list:
    """
    Search for app templates via the backend API using a provided token ID.

    This function retrieves the token ID from the request, constructs the headers,
    and makes a GET request to the EduVMStore Backend API to search for app templates.
    If the request is successful, it returns the JSON response of AppTemplates.
    In case of an error, it logs the error and returns an empty list.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: A list of app templates in JSON format or an empty list if the request fails.
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
    Fetches favorite app templates from the external API using a provided token ID.

    This function retrieves the token ID from the request, constructs the headers,
    and makes a GET request to the external API to fetch favorite app templates.
    If the request is successful, it returns the JSON response. In case of an error,
    it logs the error and returns an empty list.

    :param request: The incoming HTTP request.
    :type request: HttpRequest
    :return: A list of favorite app templates in JSON format or an empty list if the request fails.
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

class IndexView(generic.TemplateView):
    """
        Display the main index page with available app templates and associated image data.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_images_data(self):
        """
            Fetch images from the Glance API using Horizon API.
            :return: Dictionary of images indexed by image IDs.
            :rtype: dict
        """
        try:
            filters = {}
            marker = self.request.GET.get('marker', None)

            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            return {image.id: image for image in images}
        except Exception as e:
            logging.error(f"Unable to retrieve images: {e}")
            return {}

    def get_context_data(self, **kwargs):
        """
        Add AppTemplates, favorite AppTemplates, and associated image data to the context.

        This method fetches app templates and favorite app templates from the external API,
        retrieves image data from the Glance API, and adds this information to the context
        for rendering the template.

        :param kwargs: Additional context parameters.
        :return: Context dictionary with app templates, favorite app templates, and image details.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)

        app_templates = search_app_templates(self.request)
        favorite_app_templates = fetch_favorite_app_templates(self.request)

        glance_images = self.get_images_data()

        for app_template in app_templates:
            image_id = app_template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                app_template['size'] = round(glance_image.size / (1024 * 1024), 2)
                app_template['visibility'] = glance_image.visibility
            else:
                app_template['size'] = _('Unknown')
                app_template['visibility'] = _('Unknown')

        for favorite_app_template in favorite_app_templates:
            image_id = favorite_app_template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                favorite_app_template['size'] = round(glance_image.size / (1024 * 1024), 2)
                favorite_app_template['visibility'] = glance_image.visibility
            else:
                favorite_app_template['size'] = _('Unknown')
                favorite_app_template['visibility'] = _('Unknown')

        # Add favorite template IDs to context
        favorite_template_ids = [template['id'] for template in favorite_app_templates]

        context['app_templates'] = app_templates
        context['favorite_app_templates'] = favorite_app_templates
        context['favorite_template_ids'] = favorite_template_ids  # Add this line

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # If the request is AJAX, return only the table partial
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "eduvmstore_dashboard/eduvmstore/table.html", context)

        return super().get(request, *args, **kwargs)

class DetailsPageView(generic.TemplateView):
    """
    Display detailed information for a specific app template, including associated image data.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        """
        Add app template and image data to the context.
        :return: Context dictionary with app template and image details.
        """
        context = super().get_context_data(**kwargs)
        app_template = self.get_app_template()
        image_data = self.get_image_data(app_template.get('image_id', ''))
        created_at = app_template.get('created_at', '').split('T')[0]

        creator_id = app_template.get('creator_id', '')
        app_template_creator_id = creator_id.replace('-', '')
        app_template_creator_name = (
            self.get_username_from_id(app_template_creator_id)
            if app_template_creator_id else 'N/A'
        )

        context.update({
            'app_template': app_template,
            'image_visibility': image_data.get('visibility', 'N/A'),
            'image_owner': image_data.get('owner', 'N/A'),
            'app_template_creator': app_template_creator_name,
            'created_at': created_at,
        })

        return context

    def get_username_from_id(self, user_id):
        try:
            user = keystone.user_get(self.request, user_id)
            return user.name
        except Exception:
            return user_id



    def get_app_template(self):
        """
        Fetch a specific app template from the external database using token authentication.
        :return: JSON response of app template details if successful, otherwise an empty dict.
        """
        token_id = get_token_id(self.request)
        headers = {"X-Auth-Token": token_id}

        try:
            response = requests.get(
                API_ENDPOINTS['app_template_detail'].format(template_id=self.kwargs['template_id']),
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            app_template = response.json()

            # Ensure required fields exist
            app_template.setdefault('instantiation_attributes', [])
            app_template.setdefault('account_attributes', [])

            return app_template

        except requests.RequestException as e:
            logging.error("Unable to retrieve app template details: %s", e)
            return {"instantiation_attributes": [], "account_attributes": []}

    def get_image_data(self, image_id):
        """
        Fetch image details from Glance based on the image_id.
        :param image_id: ID of the image to retrieve.
        :return: Dictionary with visibility and owner details of the image.
        """
        try:
            image = glance.image_get(self.request, image_id)
            return {'visibility': image.visibility, 'owner': image.owner}
        except Exception as e:
            exceptions.handle(self.request, _('Unable to retrieve image details: %s') % str(e))
            return {}


class CreateView(generic.TemplateView):
    """
    View for creating a new app template.

    This view handles the display and submission of the form for creating a new app template.
    It processes the form data, validates it, and sends it to the backend API for creation.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'

    def get(self, request, *args, **kwargs):
            """
            Handle GET requests to render the create app template form.

            This method retrieves the context data required for rendering the form
            and returns an HTTP response with the rendered template.

            :param request: The incoming HTTP GET request.
            :type request: HttpRequest
            :param args: Additional positional arguments.
            :param kwargs: Additional keyword arguments.
            :return: Rendered HTML response.
            :rtype: HttpResponse
            """
            context = self.get_context_data()
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new app template.

        This method processes the form data submitted via POST request, validates it,
        and sends it to the backend API for creating a new app template. It handles
        the response and displays appropriate success or error messages.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: HTTP response redirecting to the index page.
        :rtype: HttpResponse
        """

        token_id = get_token_id(request)
        headers = {"X-Auth-Token": token_id}

        instantiation_attribute_raw = request.POST.get('instantiation_attributes', '').strip()
        if instantiation_attribute_raw:
            instantiation_attributes = [
                {"name": attr.strip()}
                for attr in instantiation_attribute_raw.split(':')
                if attr.strip()
            ]
        else:
            instantiation_attributes = []

        account_attribute_raw = request.POST.get('account_attributes', '').strip()
        if account_attribute_raw:
            account_attributes = [
                {"name": attr.strip()}
                for attr in account_attribute_raw.split(':')
                if attr.strip()
            ]
        else:
            account_attributes = []

        # Get security groups and convert to required format
        security_group_names = request.POST.getlist('security_groups')
        security_groups = [{"name": name} for name in security_group_names]

        data = {
            'image_id': request.POST.get('image_id'),
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'short_description': request.POST.get('short_description'),
            'instantiation_notice': request.POST.get('instantiation_notice'),
            'public': request.POST.get('public'),
            'script': request.POST.get('hiddenScriptField'),
            'instantiation_attributes': instantiation_attributes,
            'account_attributes': account_attributes,
            'version': request.POST.get('version'),
            'volume_size_gb': request.POST.get('volume_size'),
            'fixed_ram_gb': request.POST.get('fixed_ram_gb'),
            'fixed_disk_gb': request.POST.get('fixed_disk_gb'),
            'fixed_cores': request.POST.get('fixed_cores'),
            'per_user_ram_gb': request.POST.get('per_user_ram_gb'),
            'per_user_disk_gb': request.POST.get('per_user_disk_gb'),
            'per_user_cores': request.POST.get('per_user_cores'),
            'security_groups': security_groups
        }

        try:
            response = requests.post(
                API_ENDPOINTS['app_templates'],
                json=data,
                headers=headers,
                timeout=10,
            )
            if response.status_code == 201:
                messages.success(request, f"App Template created successfully.")
            else:
                logging.error(f"Unexpected response: {response.status_code}, {response.text}")
                messages.error(request, f"Failed to create App-Template. {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            messages.error(request, f"Failed to create App-Template. Please try again.")

        return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:index'))

    def get_context_data(self, **kwargs):
        """
        Add app template and image data to the context for rendering the template.

        This method fetches the app template and associated image data if a template ID is provided.
        It also retrieves a list of available images from Glance and adds this information to the context.

        :param kwargs: Additional context parameters.
        :return: Context dictionary with app template, image visibility, image owner, and available images.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)

        template_id = self.kwargs.get('template_id')
        if template_id:
            app_template = self.get_app_template(template_id)
            image_data = self.get_image_data(app_template.get('image_id', ''))
        else:
            app_template = {}
            image_data = {}

        context.update({
            'app_template': app_template,
            'image_visibility': image_data.get('visibility', 'N/A'),
            'image_owner': image_data.get('owner', 'N/A'),
            'security_groups': self.get_security_groups(),
        })

        glance_images = self.get_images_data()
        context['images'] = [(image.id, image.name) for image in glance_images]

        context['security_groups'] = self.get_security_groups()

        return context

    def get_app_template(self, template_id):
        """
        Fetch a specific app template from the external database using token authentication.

        This function retrieves the token ID from the request, constructs the headers,
        and makes a GET request to the external API to fetch the app template details.
        If the request is successful, it returns the JSON response. In case of an error,
        it logs the error and returns an empty dictionary.

        :param template_id: The ID of the app template to retrieve.
        :type template_id: str
        :return: JSON response of app template details if successful, otherwise an empty dict.
        :rtype: dict
        """
        token_id = get_token_id(self.request)
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

    def get_image_data(self, image_id):
        """
        Fetch image details from Glance based on the image_id.

        This function retrieves the image details from the Glance API using the provided image_id.
        If the image is found, it returns a dictionary containing the visibility and owner of the image.
        If an error occurs during the retrieval, it logs the error and returns an empty dictionary.

        :param image_id: ID of the image to retrieve.
        :type image_id: str
        :return: Dictionary with visibility and owner details of the image.
        :rtype: dict
        """
        try:
            image = glance.image_get(self.request, image_id)
            return {'visibility': image.visibility, 'owner': image.owner}
        except Exception as e:
            exceptions.handle(self.request, _('Unable to retrieve image details: %s') % str(e))
            return {}

    def get_security_groups(self):
        """
        Retrieve the list of available security groups using Horizon's Neutron API.

        :return: List of security group objects.
        :rtype: list
        """
        try:
            return neutron.security_group_list(self.request)
        except Exception as e:
            logging.error(f"Unable to retrieve security groups: {e}")
            return []

    def get_images_data(self):
        """
        Fetch images from the Glance API using Horizon API.

        This function retrieves a list of images available to the current tenant
        by making a call to the Glance API. It returns the list of images if successful,
        otherwise logs an error and returns an empty list.

        :return: List of images or an empty list if an error occurs.
        :rtype: list
        """
        try:
            filters = {}
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request,
                filters=filters,
                paginate=True
            )
            return images
        except Exception as e:
            logging.error(f"Unable to retrieve images: {e}")
            return []




class EditView(generic.TemplateView):
    """
    View to handle editing of an app template.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/edit.html'

    def get(self, request, *args, **kwargs):
        """
            Render the template on GET request.
            :param HttpRequest request: The incoming HTTP GET request.
            :return: Rendered HTML response.
        """
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to update an existing app template.

        This method processes the form data submitted via POST request to update an existing app template
        by sending the updated data to the backend API. It handles the extraction of instantiation and account
        attributes, constructs the data payload, and makes a PUT request to the API endpoint.

        :param request: The incoming HTTP request containing form data.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Rendered HTML response with the updated app template details or an error message.
        :rtype: HttpResponse
        """

        token_id = get_token_id(request)
        headers = {"X-Auth-Token": token_id}

        instantiation_attribute_raw = request.POST.get('instantiation_attributes', '').strip()
        if instantiation_attribute_raw:
            instantiation_attributes = [
                {"name": attr.strip()}
                for attr in instantiation_attribute_raw.split(':')
                if attr.strip()
            ]
        else:
            instantiation_attributes = []

        account_attribute_raw = request.POST.get('account_attributes', '').strip()
        if account_attribute_raw:
            account_attributes = [
                {"name": attr.strip()}
                for attr in account_attribute_raw.split(':')
                if attr.strip()
            ]
        else:
            account_attributes = []

        data = {
            'image_id': request.POST.get('image_id'),
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'short_description': request.POST.get('short_description'),
            'instantiation_notice': request.POST.get('instantiation_notice'),
            'public': request.POST.get('public'),
            'approved': request.POST.get('approved'),
            'script': request.POST.get('hiddenScriptField'),
            'instantiation_attributes': instantiation_attributes,
            'account_attributes': account_attributes,
            'version': request.POST.get('version'),
            'volume_size_gb': request.POST.get('volume_size'),
            'fixed_ram_gb': request.POST.get('fixed_ram_gb'),
            'fixed_disk_gb': request.POST.get('fixed_disk_gb'),
            'fixed_cores': request.POST.get('fixed_cores'),
            'per_user_ram_gb': request.POST.get('per_user_ram_gb'),
            'per_user_disk_gb': request.POST.get('per_user_disk_gb'),
            'per_user_cores': request.POST.get('per_user_cores'),
        }
        app_template_id = kwargs.get("template_id")  # ID aus der URL holen

        if not app_template_id:
            return JsonResponse({"error": "App Template ID is required"}, status=400)

        update_url = API_ENDPOINTS['app_templates_update'].format(template_id=app_template_id)

        try:
            response = requests.put(
                update_url,
                json=data,
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                modal_message = _("App-Template updated successfully.")
                messages.success(request, f"App Template updated successfully.")
            else:
                modal_message = _("Failed to update App-Template. Please try again.")
                logging.error(f"Unexpected response: {response.status_code}, {response.text}")
                messages.error(request, f"Failed to update App-Template. {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            modal_message = _("Failed to update App-Template. Please try again.")

        self.get_context_data(modal_message=modal_message)
        # After updating redirect to Dashboard overview
        return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:index'))

    def get_context_data(self, **kwargs):
        """
            Add app template and image data to the context.
            :param kwargs: Additional context parameters.
            :return: Context dictionary with app template and image details.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        app_template = self.get_app_template()
        image_data = self.get_image_data(app_template.get('image_id', ''))
        context.update({
            'app_template': app_template,
            'image_visibility': image_data.get('visibility', 'N/A'),
            'image_owner': image_data.get('owner', 'N/A'),
        })
        return context

    def get_app_template(self):
        """
            Fetch a specific app template from the external database using token authentication.
            :param token_id: Authentication token for API access.
            :return: JSON response of app template details if successful, otherwise an empty dict.
            :rtype: dict
        """
        token_id = get_token_id(self.request)
        headers = {"X-Auth-Token": token_id}

        try:
            response = (requests.get(API_ENDPOINTS['app_template_detail'].format(
                template_id=self.kwargs['template_id']),
                headers=headers, timeout=10))

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error("Unable to retrieve app template details: %s", e)
            return {}

    def get_image_data(self, image_id):
        """
            Fetch image details from Glance based on the image_id.
            :param image_id: ID of the image to retrieve.
            :return: Dictionary with visibility and owner details of the image.
            :rtype: dict
        """
        try:
            image = glance.image_get(self.request, image_id)
            return {'visibility': image.visibility, 'owner': image.owner}
        except Exception as e:
            exceptions.handle(self.request, _('Unable to retrieve image details: %s') % str(e))
            return {}


def generate_pdf(accounts, name, app_template, created, instantiations):
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


def generate_cloud_config(accounts, backend_script, instantiations):
    """
        Generate a cloud-config file for user account creation and backend script execution.

        This function creates a cloud-config file that includes user account information
        and a backend script.

        :param accounts: A list of dictionaries, where each dictionary contains user account details.
        :type accounts: list
        :param backend_script: string containing backend script to be included in the cloud-config file.
        :type backend_script: str
        :return: A string representing the complete cloud-config file.
        :rtype: str
        """

    sorted_keys = list(accounts[0].keys())
    sorted_keys_instantiation = list(instantiations[0].keys())

    users_content = "\n".join(
        [":".join([account.get(key, "N/A") for key in sorted_keys]) for account in accounts]
    )

    instantiations_content = "\n".join(
        [":".join([instantiation.get(key, "N/A") for key in sorted_keys_instantiation])
         for instantiation in instantiations]
    )

    cloud_config = f"""#cloud-config
write_files:
  - path: /etc/users.txt
    content: |
{generate_indented_content(users_content, indent_level=6)}
    permissions: '0644'
    owner: root:root

  - path: /etc/attributes.txt
    content: |
{generate_indented_content(instantiations_content, indent_level=6)}
    permissions: '0644'
    owner: root:root



{backend_script}
"""
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


class InstancesView(generic.TemplateView):
    """
        View for displaying instances, including form input for instance creation.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to create multiple instances.

        This method processes the form data submitted via POST request to create multiple instances
        based on the provided app template. It handles the creation of key pairs, user data,
        and metadata for each instance, and initiates the instance creation process using the Nova API.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return:HTTP response redirecting to the success page or rendering the form with error message.
        :rtype: HttpResponse
        """
        try:
            num_instances = int(request.POST.get('num_instances', 1))
            base_name = request.POST.get('instances_name')
            app_template = self.get_app_template()
            image_id = app_template.get('image_id')
            script = app_template.get('script')
            app_template_name = app_template.get('name')
            app_template_description = app_template.get('description')
            created = app_template.get('created_at', '').split('T')[0]
            volume_size = int(app_template.get('volume_size_gb') or 0)

            request.session["app_template"] = app_template_name
            request.session["created"] = created
            request.session["num_instances"] = num_instances
            request.session["base_name"] = base_name

            separate_keys = request.POST.get("separate_keys", "false").lower() == "true"
            request.session["separate_keys"] = separate_keys

            security_groups = ["default"]

            instances = []
            shared_keypair_name = f"{base_name}_shared_key"
            shared_private_key = None

            if not separate_keys:
                existing_keypairs = {kp.name for kp in nova.keypair_list(request)}
                if shared_keypair_name in existing_keypairs:
                    request.session["keypair_name"] = shared_keypair_name
                    request.session["private_key"] = None
                else:
                    keypair = nova.keypair_create(request, name=shared_keypair_name)
                    shared_private_key = keypair.private_key
                    request.session["keypair_name"] = shared_keypair_name
                    request.session["private_key"] = shared_private_key

            for i in range(1, num_instances + 1):
                instance_name = f"{base_name}-{i}"
                flavor_id = request.POST.get(f'flavor_id_{i}')
                network_id = request.POST.get(f'network_id_{i}')
                use_existing = request.POST.get(f"use_existing_volume_{i}")
                existing_volume_id = request.POST.get(f"existing_volume_id_{i}")
                create_volume_size = request.POST.get(f"volume_size_instance_{i}")
                accounts = []
                instantiations = []
                try:
                    volume_size = int(create_volume_size)
                except ValueError:
                    volume_size = 1

                no_additional_users = request.POST.get(f'no_additional_users_{i}', None)

                if no_additional_users is None:
                    try:
                        accounts = self.extract_accounts_from_form_new(request, i)
                    except Exception:
                        accounts = []

                request.session[f"accounts_{i}"] = accounts
                request.session[f"names_{i}"] = instance_name

                instantiations = self.extract_accounts_from_form_instantiation(request, i)
                request.session[f"instantiations_{i}"] = instantiations

                description = self.format_description(app_template_description)

                if not script and not accounts:
                    user_data = None
                elif not script and accounts:
                    user_data = generate_cloud_config(accounts, None, instantiations)
                elif script and no_additional_users == "on":
                    user_data = f"#cloud-config\n{script}"
                elif script and no_additional_users is None and not accounts:
                    user_data = f"#cloud-config\n{script}"
                else:
                    user_data = generate_cloud_config(accounts, script, instantiations)

                nics = [{"net-id": network_id}]
                if separate_keys:
                    keypair_name = f"{instance_name}_keypair"
                    existing_keypairs = {kp.name for kp in nova.keypair_list(request)}

                    if keypair_name in existing_keypairs:
                        request.session[f"keypair_name_{i}"] = keypair_name
                        request.session[f"private_key_{i}"] = None
                    else:
                        keypair = nova.keypair_create(request, name=keypair_name)
                        private_key = keypair.private_key
                        request.session[f"keypair_name_{i}"] = keypair_name
                        request.session[f"private_key_{i}"] = private_key
                else:
                    keypair_name = shared_keypair_name

                metadata = {"App_Template": app_template_name}
                for index, account in enumerate(accounts):
                    user_data_account = ", ".join([f"{key}: {value}" for key, value in account.items()])
                    metadata[f"User_{index + 1}"] = user_data_account
                for index, instantiation in enumerate(instantiations):

                    parts = []
                    current_part = ""
                    for kv_pair in [f"{key}: {value}" for key, value in instantiation.items()]:

                        if len(current_part) + len(kv_pair) + 2 > 255:
                            parts.append(current_part.rstrip(", "))
                            current_part = ""
                        current_part += kv_pair + ", "
                    if current_part:
                        parts.append(current_part.rstrip(", "))

                    for part_index, part_content in enumerate(parts):
                        key = f"Instantiation_{index+1}_Part{part_index+1}"
                        metadata[key] = part_content

                block_device_mapping_v2 = []
                if use_existing == "existing" and existing_volume_id:
                    block_device_mapping_v2.append({
                        "boot_index": -1,
                        "uuid": existing_volume_id,
                        "source_type": "volume",
                        "destination_type": "volume",
                        "delete_on_termination": True,
                        "device_name": "/dev/vdb",
                    })
                    logging.info(f"Attach existing Volume {existing_volume_id} to {instance_name}")
                # OpenStack only allows Volumes larger than 1 GB
                elif use_existing == "new" and volume_size >= 1:

                    volume_name = f"{instance_name}-volume"
                    # Create Volume via Cinder
                    volume = cinder.volume_create(
                        request,
                        size=volume_size,
                        name=volume_name,
                        description=f"Extra volume for {instance_name}",
                        volume_type="__DEFAULT__"
                    )
                    volume = self.wait_for_volume_available(request, volume.id)

                    # Attach an additional block device (a virtual disk) to the instance.
                    block_device_mapping_v2.append({
                        "boot_index": -1,
                        "uuid": volume.id,
                        "source_type": "volume",
                        "destination_type": "volume",
                        "delete_on_termination": True,
                        "device_name": "/dev/vdb",
                    })
                else:
                    logging.info(f"{instance_name} is without additional volume")






                nova.server_create(
                    request,
                    name=instance_name,
                    image=image_id,
                    flavor=flavor_id,
                    key_name=keypair_name,
                    user_data=user_data,
                    security_groups=security_groups,
                    nics=nics,
                    meta=metadata,
                    description=description,
                    block_device_mapping_v2=block_device_mapping_v2,
                )
                instances.append(instance_name)

            return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:success'))

        except Exception as e:
            logging.error(f"Failed to create instances: {e}")
            modal_message = _(f"Failed to create instances. Error: {e}")

        context = self.get_context_data(modal_message=modal_message)
        return render(request, self.template_name, context)

    def wait_for_volume_available(self, request, volume_id, timeout=60):
        """
        Wait for a volume to become available within a specified timeout period.

        This function repeatedly checks the status of a volume until it becomes available
        or an error occurs. If the volume does not become available within the timeout period,
        a TimeoutError is raised.

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param volume_id: The ID of the volume to check.
        :type volume_id: str
        :param timeout: The maximum time to wait for the volume to become available, in seconds.
        :type timeout: int
        :return: The volume object if it becomes available.
        :rtype: Volume
        :raises TimeoutError: If the volume does not become available within the timeout period.
        :raises Exception: If the volume status is 'error'.
        """
        for i in range(timeout):
            volume = cinder.volume_get(request, volume_id)
            if volume.status == "available":
                return volume
            elif volume.status == "error":
                raise Exception(f"Volume {volume_id} failed to build.")
            time.sleep(1)
        raise TimeoutError(f"Timeout while waiting for volume {volume_id} to become available.")


    def get_context_data(self, **kwargs):
        """
            Add form and optional image ID to the context for rendering the template.

            :param kwargs: Additional context parameters.
            :return: Context dictionary containing the form and image ID if specified.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        app_template_id = self.kwargs['image_id']
        app_template = self.get_app_template()

        # Fetch available flavors from Nova
        context['flavors'] = self.get_flavors(app_template)

        # Context for the selected AppTemplate --> Display system infos
        context['app_template'] = app_template

        # Fetch available networks
        context['networks'] = self.get_networks()

        # Include the app_template_id in the context
        context['app_template_id'] = app_template_id

        context['expected_account_fields'] = self.get_expected_fields()

        context['expected_instantiation_fields'] = self.get_expected_fields_instantiation()

        context['volume_size'] =  int(app_template.get('volume_size_gb') or 0)

        volumes = cinder.volume_list(self.request)
        attachable_volumes = [volume for volume in volumes if volume.status == "available"]
        context['attachable_volumes'] = attachable_volumes

        has_attachable_volumes = len(attachable_volumes) > 0
        context['hasAttachableVolumes'] = has_attachable_volumes



        return context

    # def get_flavors(self, ):
    #  """Fetch flavors from Nova to correlate instances."""
    # try:
    #     flavors = api.nova.flavor_list(self.request)
    #     return {str(flavor.id): flavor.name for flavor in flavors}
    # except Exception:
    #     exceptions.handle(self.request, ignore=True)
    #     return {}

    def get_flavors(self, app_template):
        """
        Fetch all available flavors from Nova and filter them based on the system requirements
        specified in the app template.

        :param app_template: The app template containing system requirements.
        :type app_template: dict
        :return: A dictionary containing all flavors, suitable flavors, and the selected flavor.
        :rtype: dict
        """
        try:
            flavors = api.nova.flavor_list(self.request)
            if not flavors:
                logging.error("No flavors returned from Nova API.")
                return {}

            flavor_dict = {str(flavor.id): flavor for flavor in flavors}
            logging.info(f"Found {len(flavors)} flavors.")

            suitable_flavors = {}

            for flavor_id, flavor in flavor_dict.items():
                    suitable_flavors[flavor_id] = {
                        'name': flavor.name,
                        'ram': flavor.ram,
                        'disk': flavor.disk,
                        'cores': flavor.vcpus
                    }

            if not suitable_flavors:
                logging.warning("No suitable flavors found for the given requirements.")


            result = {
                'flavors': {flavor_id: flavor.name for flavor_id, flavor in flavor_dict.items()},
                  'suitable_flavors': suitable_flavors
            }

            logging.info(f"Returning flavor data: {result}")
            return result

        except Exception as e:
            logging.error(f"An error occurred while fetching flavors: {e}")
            return {}



    def get_expected_fields(self):
        """
        Retrieve the expected fields for account creation from the app template.

        This function fetches the app template and extracts the account attributes,
        which are the expected fields for account creation.

        :return: A list of expected field names for account creation.
        :rtype: list
        """
        app_template = self.get_app_template()

        account_attributes = app_template.get('account_attributes')

        account_attribute = [attr['name'] for attr in account_attributes]
        return account_attribute

    def extract_accounts_from_form_new(self, request, instance_id):
        """
        Extract account information from the form data for a specific instance.

        This function retrieves the expected fields for account creation, extracts the corresponding
        data from the POST request for the specified instance, and compiles it into a list of account
        dictionaries.

        :param request: The incoming HTTP request containing form data.
        :type request: HttpRequest
        :param instance_id: The ID of the instance for which to extract account data.
        :type instance_id: int
        :return: A list of dictionaries, each containing account information for the specified instance.
        :rtype: list
        """
        accounts = []
        expected_fields = self.get_expected_fields()

        extracted_data = {
            field: request.POST.getlist(f"{field}_{instance_id}[]")
            for field in expected_fields
        }

        num_entries = len(next(iter(extracted_data.values()), []))

        for i in range(num_entries):
            account = {field: extracted_data[field][i] for field in expected_fields}
            accounts.append(account)

        return accounts

    def get_expected_fields_instantiation(self):
        """
        Retrieve the expected fields for account creation from the app template.

        This function fetches the app template and extracts the instantiation attributes,
        which are the expected fields for account creation.

        :return: A list of expected field names for account creation.
        :rtype: list
        """
        app_template = self.get_app_template()

        instantiation_attributes = app_template.get('instantiation_attributes')

        instantiation_attribute = [attr['name'] for attr in instantiation_attributes]
        return instantiation_attribute

    def extract_accounts_from_form_instantiation(self, request, instance_id):
        """
        Extract account information from the form data for a specific instance.

        This function retrieves the expected fields for account creation, extracts the corresponding
        data from the POST request for the specified instance, and compiles it into a list of account
        dictionaries.

        :param request: The incoming HTTP request containing form data.
        :type request: HttpRequest
        :param instance_id: The ID of the instance for which to extract account data.
        :type instance_id: int
        :return: A list of dictionaries, each containing account information for the specified instance.
        :rtype: list
        """
        instantiations = []
        expected_fields_instantiation = self.get_expected_fields_instantiation()

        extracted_data_instantiations = {
            field: request.POST.getlist(f"{field}_{instance_id}_instantiation[]")
            for field in expected_fields_instantiation
        }

        num_entries = len(next(iter(extracted_data_instantiations.values()), []))

        for i in range(num_entries):
            instantiation = {field: extracted_data_instantiations[field][i]
                             for field in expected_fields_instantiation}
            instantiations.append(instantiation)

        return instantiations

    def get_networks(self):
        """
        Fetch networks from Neutron for the current tenant.

        This function retrieves the list of networks available to the current tenant
        by making a call to the Neutron API. It returns a dictionary mapping network
        IDs to network names.

        :return: A dictionary where the keys are network IDs and the values are network names.
        :rtype: dict
        """
        try:
            tenant_id = self.request.user.tenant_id
            networks = api.neutron.network_list_for_tenant(self.request, tenant_id)
            return {network.id: network.name for network in networks}
        except Exception as e:
            logging.error(f"Unable to fetch networks: {e}")
            return {}

    # Get AppTemplate Details to display while launching an instance
    def get_app_template(self):
        """
            Fetch a specific app template from the external database using token authentication.
            :param token_id: Authentication token for API access.
            :return: JSON response of app template details if successful, otherwise an empty dict.
            :rtype: dict
        """
        token_id = get_token_id(self.request)
        headers = {"X-Auth-Token": token_id}

        try:
            response = (requests.get(API_ENDPOINTS['app_template_detail'].format(
                template_id=self.kwargs['image_id']),
                headers=headers, timeout=10))

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error("Unable to retrieve app template details: %s", e)
            return {}

    def format_description(self, description):
        """
    Format the given description by removing extra whitespace and truncating it to a maximum length.

    This function removes any extra whitespace from the description and ensures that the resulting
    string does not exceed 255 characters in length.

    :param description: The description string to be formatted.
    :type description: str
    :return: The formatted description string.
    :rtype: str
    """
        description = re.sub(r'\s+', ' ', description)
        description = description[:255]
        return description


class InstanceSuccessView(generic.TemplateView):
    template_name = "eduvmstore_dashboard/eduvmstore/success.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the success template.

        :param request: The incoming HTTP GET request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        :return: Rendered HTML response.
        :rtype: HttpResponse
        """
        return render(request, self.template_name)

    class DownloadInstanceDataView(generic.View):
        """
        View to generate and return a ZIP file containing:
        - PDFs with instance user account information
        - Private keys (either one shared key or separate keys per instance)
        """

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to generate and return a ZIP file containing PDFs with
        instance user account information and private keys (either one shared key or
        separate keys per instance).

        :param request: The incoming HTTP request.
        :type request: HttpRequest
        :param args: Additional positional arguments.
        :type args: tuple
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: An HTTP response with the generated ZIP file.
        :rtype: HttpResponse
        """
        num_instances = int(request.session.get("num_instances", 1))
        separate_keys = request.session.get("separate_keys", False)
        base_name = request.session.get("base_name", "instance")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

            for i in range(1, num_instances + 1):
                accounts = request.session.get(f"accounts_{i}", [])
                name = request.session.get(f"names_{i}", f"Instance-{i}")
                app_template = request.session.get("app_template", "Unknown")
                created = request.session.get("created", "Unknown Date")
                instantiation = request.session.get(f"instantiations_{i}", [])

                if accounts or instantiation:
                    pdf_content = generate_pdf(accounts, name, app_template, created, instantiation)
                    zip_file.writestr(f"{name}.pdf", pdf_content)

            if not separate_keys:
                private_key = request.session.get("private_key")
                keypair_name = request.session.get("keypair_name", "shared_instance_key")
                if private_key:
                    zip_file.writestr(f"{keypair_name}.pem", private_key)


            else:
                for i in range(1, num_instances + 1):
                    private_key = request.session.get(f"private_key_{i}")
                    keypair_name = request.session.get(f"keypair_name_{i}", f"instance_key_{i}")
                    if private_key:
                        zip_file.writestr(f"{keypair_name}.pem", private_key)

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{base_name}_data.zip"'

        for i in range(1, num_instances + 1):
            request.session.pop(f"accounts_{i}", None)
            request.session.pop(f"instantiations_{i}", None)
            request.session.pop(f"names_{i}", None)
            request.session.pop(f"private_key_{i}", None)
            request.session.pop(f"keypair_name_{i}", None)

        request.session.pop("private_key", None)
        request.session.pop("keypair_name", None)
        request.session.pop("separate_keys", None)
        request.session.pop("num_instances", None)
        request.session.pop("app_template", None)
        request.session.pop("created", None)
        request.session.pop("base_name", None)

        return response

class GetFavoriteAppTemplateView(generic.View):

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to mark an app template as a favorite via the external API.

        This method retrieves the app template ID and name from the POST request,
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
        Handle POST requests to delete a favorite app template via the external API.

        This method retrieves the app template ID and name from the POST request,
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
    """Handles app template deletion.
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