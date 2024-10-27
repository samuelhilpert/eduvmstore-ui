import requests
import socket
import logging
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from horizon import tabs, exceptions
from openstack_dashboard.api import glance
from django.views import generic
from myplugin.content.eduvmstore.forms import AppTemplateForm, InstanceForm
from django.utils.translation import gettext_lazy as _

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

def fetch_app_templates(token_id):
    """
        Fetches app templates from the external API using a provided token ID.
        :param token_id: The authentication token for API access.
        :return: List of app templates if the request is successful, otherwise an empty list.
        :rtype: list
    """
    headers = {"X-Auth-Token": token_id}
    try:
        response = requests.get("http://localhost:8000/api/app-templates/", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch app templates: {e}")
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
        token_id = self.request.GET.get('token_id')

        app_templates = fetch_app_templates(token_id)

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

def get_image_details_via_rest(token_id, image_id):
    """
        Fetch image details via REST API using provided token and image ID.
        :param token_id: Authentication token for API access.
        :param image_id: ID of the image to retrieve.
        :return: JSON response of image details if successful, otherwise None.
        :rtype: dict or None
    """
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get(f"http://{get_host_ip()}/image/v2/images/{image_id}",
                                headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching image details: {err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error contacting the Glance API: {e}")
        return None


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
        context = super(DetailsPageView, self).get_context_data(**kwargs)
        token_id = self.request.GET.get('token_id')
        app_template = self.get_app_template(token_id)
        image_data = self.get_image_data(app_template['image_id'])


        context['app_template'] = app_template
        context['image_visibility'] = image_data.get('visibility', 'N/A')
        context['image_owner'] = image_data.get('owner', 'N/A')
        return context

    def get_app_template(self,token_id):
        """
            Fetch a specific app template from the external database using token authentication.
            :param token_id: Authentication token for API access.
            :return: JSON response of app template details if successful, otherwise an empty dict.
            :rtype: dict
        """
        headers = {"X-Auth-Token": token_id}

        try:
            app_template_id = self.kwargs['template_id']  # Assuming template_id is in the URL
            response = requests.get(
            f"http://localhost:8000/api/app-templates/{app_template_id}",
            headers=headers,
            timeout=10)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            exceptions.handle(self.request, _('Unable to retrieve app template details: %s') % str(e))
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
    success_url = reverse_lazy('')  # Specify a success URL

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
        token_id = request.GET.get('token_id')  # Retrieve token_id from POST data
        if not token_id:
            logging.error("Token ID is required but missing in the POST request.")
            context = self.get_context_data()
            context['error'] = _("Token ID is required but missing.")
            return render(request, self.template_name, context)

        headers = {"X-Auth-Token": token_id}

        data = {
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
            response = requests.post(
                "http://localhost:8000/api/app-templates/",
                json=data,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()  # Raise an error for bad responses
            return redirect(self.success_url)  # Redirect to success URL
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

    def get_context_data(self, **kwargs):
        """
            Add form and optional image ID to the context for rendering the template.

            :param kwargs: Additional context parameters.
            :return: Context dictionary containing the form and image ID if specified.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context['form'] = InstanceForm()

        image_id = self.request.GET.get('image_id')
        if image_id:
            context['image_id'] = image_id

        return context

