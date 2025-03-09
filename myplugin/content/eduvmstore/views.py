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
from openstack_dashboard.api import glance, nova
from django.views import generic
from myplugin.content.eduvmstore.forms import AppTemplateForm, InstanceForm
from django.utils.translation import gettext_lazy as _
from myplugin.content.api_endpoints import API_ENDPOINTS
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from django.urls import reverse
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
    Retrieves the token ID from the request object.
    """
    return getattr(getattr(request, "user", None), "token", None) and request.user.token.id


def fetch_app_templates(request):
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


def validate_name(request):
    if request.method == "POST":
        try:
            # JSON-Body auslesen
            body = json.loads(request.body)
            name = body.get('name', '').strip()

            # Token-ID abrufen
            token_id = get_token_id(request)
            headers = {"X-Auth-Token": token_id}

            # API-Aufruf an das Backend
            url = f"{API_ENDPOINTS['check_name']}{name}/collisions"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Antwort verarbeiten
            data = response.json()
            is_valid = not data.get('collisions', True)

        except (requests.RequestException, ValueError, json.JSONDecodeError):
            is_valid = False

        return JsonResponse({'valid': is_valid})

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
            Add app templates and image data to the context.
            :param kwargs: Additional context parameters.
            :return: Context dictionary with app templates and image details.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        #token_id = self.request.GET.get('token_id')

        app_templates = fetch_app_templates(self.request)

        glance_images = self.get_images_data()

        for template in app_templates:
            image_id = template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                template['size'] = round(glance_image.size / (1024 * 1024), 2)
                template['visibility'] = glance_image.visibility
            else:
                template['size'] = _('Unknown')
                template['visibility'] = _('Unknown')

        context['app_templates'] = app_templates

        return context

class DetailsPageView(generic.TemplateView):
    """
        Display detailed information for a specific app template, including associated image data.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'
    page_title = "{{ app_template.name }}"

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


class CreateView(generic.TemplateView):
    """
        View to handle the creation of a new app template with specified details.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'
    #success_url = reverse_lazy('/eduvmstore_dashboard/')

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
        Handle POST requests to create a new app template by sending data to the backend API.
        """
        token_id = get_token_id(request)
        headers = {"X-Auth-Token": token_id}

        account_structure_raw = request.POST.get('account_structure', '').strip()
        if account_structure_raw:
            account_attributes = [
                {"name": attr.strip()}
                for attr in account_structure_raw.split(':')
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
            'script': request.POST.get('hiddenScriptField'),
            'account_attributes' : account_attributes,
            'public': request.POST.get('public'),
            'version': request.POST.get('version'),
            'fixed_ram_gb': request.POST.get('fixed_ram_gb'),
            'fixed_disk_gb': request.POST.get('fixed_disk_gb'),
            'fixed_cores': request.POST.get('fixed_cores'),
            'per_user_ram_gb': request.POST.get('per_user_ram_gb'),
            'per_user_disk_gb': request.POST.get('per_user_disk_gb'),
            'per_user_cores': request.POST.get('per_user_cores'),

        }

        try:
            response = requests.post(
                API_ENDPOINTS['app_templates'],
                json=data,
                headers=headers,
                timeout=10,
            )
            if response.status_code == 201:
                modal_message = _("App-Template created successfully.")
                messages.success(request, f"App Template created successfully.")
            else:
                modal_message = _("Failed to create App-Template. Please try again.")
                logging.error(f"Unexpected response: {response.status_code}, {response.text}")
                messages.error(request, f"Failed to create App-Template. {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            modal_message = _("Failed to create App-Template. Please try again.")


        context = self.get_context_data(modal_message=modal_message)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        """
            Add available images to the context for template selection.
            :param kwargs: Additional context parameters.
            :return: Context dictionary with available images.
            :rtype: dict
        """
        context = {}
        glance_images = self.get_images_data()
        context['images'] = [(image.id, image.name) for image in glance_images]
        return context

    def get_images_data(self):
        """
        Fetch the images from the Glance API using the Horizon API.

        :return: List of images retrieved from Glance, or an empty list if retrieval fails.
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


def generate_pdf(accounts, name):
    """
    Generate a PDF document containing user account information for a created instance.

    This function creates a PDF file with a list of user accounts and their details for a specified instance.
    The PDF is generated using the ReportLab library and returned as an HTTP response.

    :param accounts: A list of dictionaries, where each dictionary contains user account details.
    :type accounts: list
    :param name: The name of the created instance.
    :type name: str
    :return: An HTTP response containing the generated PDF file.
    :rtype: HttpResponse
    """

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("User Credentials")

    pdf.drawString(100, 750, f"User accounts for the created instance {name}:")
    y = 730

    all_keys = set()
    for account in accounts:
        all_keys.update(account.keys())

    all_keys = sorted(all_keys)

    pdf.drawString(100, y, " | ".join(all_keys))
    y -= 20
    pdf.drawString(100, y, "-" * 100)
    y -= 20

    for account in accounts:
        row_values = [account.get(key, "N/A") for key in all_keys]
        pdf.drawString(100, y, " | ".join(row_values))
        y -= 20

        if y < 50:
            pdf.showPage()
            y = 750

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=userdata.pdf"
    return response

def generate_cloud_config(accounts,backend_script):
    """
        Generate a cloud-config file for user account creation and backend script execution.

        This function creates a cloud-config file that includes user account information and a backend script.

        :param accounts: A list of dictionaries, where each dictionary contains user account details.
        :type accounts: list
        :param backend_script: A string containing the backend script to be included in the cloud-config file.
        :type backend_script: str
        :return: A string representing the complete cloud-config file.
        :rtype: str
        """

    sorted_keys = list(accounts[0].keys())

    users_content = "\n".join(
        [":".join([account.get(key, "N/A") for key in sorted_keys]) for account in accounts]
    )

    cloud_config = f"""#cloud-config
write_files:
  - path: /etc/users.txt
    content: |
{generate_indented_content(users_content, indent_level=6)}
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
     Handle POST requests to create a new instance with specified details.

     This method extracts necessary data from the POST request, generates a cloud-config script,
     and creates a new instance using the Nova API. It also handles session data for accounts
     and instance name, and formats the instance description.

     :param request: The incoming HTTP POST request.
     :type request: HttpRequest
     :param args: Additional positional arguments.
     :param kwargs: Additional keyword arguments.
     :return: An HTTP redirect to the success page or a rendered template with an error message.
     :rtype: HttpResponse
     """

        try:

            flavor_id = request.POST.get('flavor_id')
            name = request.POST.get('instances_name')
            network_id = request.POST.get('network_id')


            app_template = self.get_app_template()
            image_id = app_template.get('image_id')
            script = app_template.get('script')
            app_template_name = app_template.get('name')
            app_template_descritpion = app_template.get('description')

            accounts = self.extract_accounts_from_form_new(request)
            request.session["accounts"] = accounts
            request.session["instance_name"] = name

            description = self.format_description(app_template_descritpion)


            user_datas = generate_cloud_config(accounts, script)

            nics = [{"net-id": network_id}]

            key_name = None
            security_groups = ["default"]

            metadata = {"app_template": app_template_name}

            for index, account in enumerate(accounts):
                user_data = ", ".join([f"{key}: {value}" for key, value in account.items()])
                metadata[f"user_{index+1}"] = user_data



            nova.server_create(
                request,
                name=name,
                image=image_id,
                flavor=flavor_id,
                key_name=key_name,
                user_data=user_datas,
                security_groups=security_groups,
                nics=nics,
                meta=metadata,
                description=description,
            )

            return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:success'))

        except Exception as e:
            logging.error(f"Failed to create instance: {e}")
            modal_message = _(f"Failed to create instance. Error: {e}")


        context = self.get_context_data(modal_message=modal_message)
        return render(request, self.template_name, context)


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
        context['flavors'] = self.get_flavors()

        #Context for the selected App-Template --> Display system infos
        context['app_template'] = app_template

        # Fetch available networks
        context['networks'] = self.get_networks()

        # Include the app_template_id in the context
        context['app_template_id'] = app_template_id

        context['expected_account_fields'] = self.get_expected_fields()

        return context

    def get_flavors(self, ):
        """Fetch flavors from Nova to correlate instances."""
        try:
            flavors = api.nova.flavor_list(self.request)
            return {str(flavor.id): flavor.name for flavor in flavors}
        except Exception:
            exceptions.handle(self.request, ignore=True)
            return {}

    def extract_accounts_from_form(self, request):
        """Extract account details from the POST
        form and format them as dictionaries with matching usernames and passwords."""
        accounts = []

        account_names = request.POST.getlist('account_name')
        account_passwords = request.POST.getlist('account_password')

        for name, password in zip(account_names, account_passwords):
            if name and password:
                accounts.append({
                    "username": name,
                    "password": password
                })

        return accounts

    def get_expected_fields(self):

        app_template = self.get_app_template()
        account_structure = app_template.get('account_attributes')

        account_attribute = [attr['name'] for attr in account_structure]
        return account_attribute

    def extract_accounts_from_form_new(self, request):
        accounts = []
        expected_fields = self.get_expected_fields()  # Erwartete Felder holen

        extracted_data = {field: request.POST.getlist(field) for field in expected_fields}
        # extracted_data = {"account_name": ["Alice", "Bob"],"account_password": ["pass123", "secure456"]}

        num_entries = len(next(iter(extracted_data.values())))

        for i in range(num_entries):
            account = {field: extracted_data[field][i] for field in expected_fields}
            accounts.append(account)

        return accounts

    def get_networks(self):
        """Fetch networks from Neutron for the current tenant."""
        try:
            tenant_id = self.request.user.tenant_id
            networks = api.neutron.network_list_for_tenant(self.request, tenant_id)
            return {network.id: network.name for network in networks}
        except Exception as e:
            logging.error(f"Unable to fetch networks: {e}")
            return {}

    #Get App Template Details to display while launching an instance
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

    def format_description(self,description):
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
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        accounts = request.session.get("accounts", [])
        name = request.session.get("instance_name", [])
        pdf_response = generate_pdf(accounts, name)
        del request.session["accounts"]
        del request.session["instance_name"]
        return pdf_response
