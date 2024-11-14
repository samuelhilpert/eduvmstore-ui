import requests
import socket
import logging

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
    token_id = get_token_id(request)  # Assumes token ID is always present
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(API_ENDPOINTS['app_templates'],  # Use the centralized endpoint
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error("Failed to fetch app templates: %s", e)
        return []

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
            filters = {}  # Add any filters if needed
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
        token_id = get_token_id(self.request)  # Assumes token ID is always present
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
    #success_url = reverse_lazy('/eduvmstore_dashboard/')  # Specify a success URL

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
            :param HttpRequest request: The incoming HTTP POST request.
            :return: Redirect response to success URL if successful, or re-rendered template with error.
        """
        token_id = get_token_id(request)  # Assumes token ID is always present
        headers = {"X-Auth-Token": token_id}

        data = {
            #creator_id should be changed
            'creator_id': "1d268016-2c68-4d58-ab90-268f4a84f39d",  # Example creator ID
            'image_id': request.POST.get('image_id'),
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'short_description': request.POST.get('short_description'),
            'instantiation_notice': request.POST.get('instantiation_notice'),
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
            # Send the data to the API
            response = requests.post(API_ENDPOINTS['app_templates'],
                                     json=data,
                                     headers=headers,
                                     timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            # After successful instance launch, redirect to the homepage
            return redirect('')
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to create app template: {e}")
            context = self.get_context_data()
            context['error'] = _("Failed to create app template. Please try again.")
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
            return images  # Return the list of images
        except Exception as e:
            logging.error(f"Unable to retrieve images: {e}")
            return []

class InstancesView(generic.TemplateView):
    """
        View for displaying instances, including form input for instance creation.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'
   # success_url = reverse_lazy('/')  # Redirect to the index page upon success

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        #app_template_id = self.kwargs['image_id']  # Assuming template_id is in the URL
        #flavor_id = request.POST.get('flavor_id')
        #instance_name = request.POST.get('name')
       # no_additional_users = request.POST.get('no_additional_users') is not None

       # token_id = None
      #  if hasattr(request, "user") and hasattr(request.user, "token"):
        #    token_id = request.user.token.id
       # else:
       #     return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=401)

        #headers = {"X-Auth-Token": token_id}

        # If "No additional users" is not checked, collect the account data
        #accounts = self.extract_accounts_from_form(self.request)

    # Retrieve and log the token
        #token_id = get_token_id(request)
        #logging.debug(f"Token ID: {token_id}")  # Only use debug level for sensitive info

        #headers = {"X-Auth-Token": token_id}

        # Prepare the payload for creating an instance
        data = {
            'app_template_id': self.kwargs['image_id'],
            'flavor_id':  request.POST.get('flavor_id'),
            'name': request.POST.get('name'),
            #'accounts': self.extract_accounts_from_form(request)
        }

        try:
            # Send the data to the backend to create an instance
            response = requests.post(API_ENDPOINTS['instances_launch'],
                                     json=data,
                                 #    headers=headers,
                                     timeout=10)
            response.raise_for_status()  # Raise an error for bad responses
            # After successful instance launch, redirect to the homepage
            return redirect('')  # Redirect to the success URL

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to launch instance: {e}")
            context = self.get_context_data()
            context['error'] = _("Failed to launch instance. Please try again.")
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        """
            Add form and optional image ID to the context for rendering the template.

            :param kwargs: Additional context parameters.
            :return: Context dictionary containing the form and image ID if specified.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
       # token_id = self.request.GET.get('token_id')
        app_template_id = self.kwargs['image_id']  # Assuming template_id is in the URL

        # Fetch available flavors from Nova
        context['flavors'] = self.get_flavors()

        # Include the app_template_id in the context
        context['app_template_id'] = app_template_id
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
        """Extract account details from the POST form and format them as dictionaries with matching usernames and passwords."""
        accounts = []

        # Get account names and passwords from the POST request
        account_names = request.POST.getlist('account_name')
        account_passwords = request.POST.getlist('account_password')

        # Create a dictionary for each account
        for name, password in zip(account_names, account_passwords):
            if name and password:  # Ensure username matches password
                accounts.append({
                    "username": name,
                    "password": password
                })

        return accounts