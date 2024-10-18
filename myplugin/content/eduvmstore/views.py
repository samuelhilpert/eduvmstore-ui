import requests

import socket
import logging

from django.shortcuts import render
from horizon import tabs

from openstack_dashboard.api import glance
from django.views import generic
from myplugin.content.eduvmstore import tabs as edu_tabs
from myplugin.content.eduvmstore.forms import AppTemplateForm, InstanceForm

from django.utils.translation import gettext_lazy as _

def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        raise RuntimeError("Failed to retrieve host IP address") from e
    finally:
        s.close()
    return ip

def fetch_app_templates():
    try:
        response = requests.get("http://localhost:8000/api/app-templates/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch app templates: {e}")
        return []


class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_images_data(self):
        """Fetch the images from the Glance API using the Horizon API."""
        try:
            filters = {}  # Add any filters if needed
            marker = self.request.GET.get('marker', None)

            # Use glance.image_list_detailed from Horizon API
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # Return images and pagination details
            return {image.id: image for image in images}
        except Exception as e:
            logging.error(f"Unable to retrieve images: {e}")
            return {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch app templates from external database
        app_templates = fetch_app_templates()

        # Fetch image data from Glance
        glance_images = self.get_images_data()

        # Combine app template data with corresponding Glance image data
        for template in app_templates:
            image_id = template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                template['size'] = glance_image.size
                template['visibility'] = glance_image.visibility
            else:
                template['size'] = _('Unknown')
                template['visibility'] = _('Unknown')

        context['app_templates'] = app_templates
        return context

def get_image_details_via_rest(request, image_id):
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
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_id = self.kwargs.get('image_id')

        if image_id:
            image_details = get_image_details_via_rest(self.request, image_id)
            if image_details:
                context['image'] = image_details
            else:
                context['error'] = _("Could not retrieve image details.")
        else:
            context['error'] = _("No image ID provided.")

        return context


class CreateView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AppTemplateForm()
        return context

class InstancesView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InstanceForm()

        image_id = self.request.GET.get('image_id')
        if image_id:
            context['image_id'] = image_id

        return context
