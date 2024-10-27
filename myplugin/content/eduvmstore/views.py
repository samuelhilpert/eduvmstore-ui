import requests
import socket
import logging

from django.shortcuts import render
from horizon import tabs, exceptions
from openstack_dashboard.api import glance
from django.views import generic
from myplugin.content.eduvmstore import tabs as edu_tabs
from myplugin.content.eduvmstore.forms import AppTemplateForm, InstanceForm

from django.utils.translation import gettext_lazy as _

def get_host_ip():
    """
    Retrieve the host IP address.

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


def fetch_app_templates(token_id):
    """
    Fetch app templates from database.

    :param str token_id: The Keystone authentication token.
    :return: A list of app templates.
    :rtype: list[dict]
    """
    headers = {"X-Auth-Token": token_id}
    try:
        response = requests.get("http://192.168.64.1:8000/api/app-templates/", headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch app templates: {e}")
        return []


class IndexView(generic.TemplateView):
    """
    View to display the main dashboard index page.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_images_data(self):
        """
        Retrieve images from the Glance service using the Horizon API.

        :return: A dictionary of image data mapped by image ID.
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
        Populate the context with app template and image data.

        :return: Context dictionary with app templates and image details.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

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


def get_image_details_via_rest(request, image_id):
    """
    Retrieve image details from Glance using a REST API call.

    :param str image_id: The ID of the image to retrieve.
    :return: JSON response containing image details if successful, else None.
    :rtype: dict or None
    """
    headers = {"X-Auth-Token": request.user.token.id}
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
    View to display details for a specific app template and its image.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'
    page_title = "{{ app_template.name }}"

    def get_context_data(self, **kwargs):
        """
        Populate context with app template and image details.

        :return: Context dictionary containing app template and image information.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        app_template = self.get_app_template()
        image_data = self.get_image_data(app_template['image_id'])

        context['app_template'] = app_template
        context['image_visibility'] = image_data.get('visibility', 'N/A')
        context['image_owner'] = image_data.get('owner', 'N/A')
        return context

    def get_app_template(self):
        """
        Retrieve a specific app template based on its ID.

        :param str template_id: The ID of the app template, obtained from the URL parameters.
        :return: JSON response with app template data if successful, else an empty dict.
        :rtype: dict
        """
        try:
            app_template_id = self.kwargs['template_id']
            response = requests.get(f"http://localhost:8000/api/app-templates/{app_template_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            exceptions.handle(self.request, _('Unable to retrieve app template details: %s') % str(e))
            return {}

    def get_image_data(self, image_id):
        """
        Retrieve image details from Glance based on the image ID.

        :param str image_id: The ID of the image to retrieve.
        :return: Dictionary with image visibility and owner.
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
    View to display the form for creating a new app template.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'

    def get_context_data(self, **kwargs):
        """
        Add the app template form to the context.

        :return: Context dictionary with the app template form.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context['form'] = AppTemplateForm()
        return context


class InstancesView(generic.TemplateView):
    """
    View to display the instance creation form.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'

    def get_context_data(self, **kwargs):
        """
        Add the instance form and the image ID to the context.

        :return: Context dictionary with the instance form and image ID.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        context['form'] = InstanceForm()

        image_id = self.request.GET.get('image_id')
        if image_id:
            context['image_id'] = image_id

        return context
