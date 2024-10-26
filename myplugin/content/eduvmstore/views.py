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

# Retrieve the host IP address
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


# Fetch app templates from database
def fetch_app_templates(token_id):
    headers = {"X-Auth-Token": token_id}

    try:
        response = requests.get("http://192.168.64.1:8000/api/app-templates/", headers=headers, timeout=10)
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
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        # Fetch app templates from external database
        app_templates = fetch_app_templates(token_id)

        # Fetch image data from Glance
        glance_images = self.get_images_data()

        # Combine app template data with corresponding Glance image data
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

# Fetch image details from Glance using REST API
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
    page_title = "{{ app_template.name }}"

    # Fetch the app template and image details
    def get_context_data(self, **kwargs):
        context = super(DetailsPageView, self).get_context_data(**kwargs)
        app_template = self.get_app_template()
        image_data = self.get_image_data(app_template['image_id'])

        context['app_template'] = app_template
        context['image_visibility'] = image_data.get('visibility', 'N/A')
        context['image_owner'] = image_data.get('owner', 'N/A')
        return context

    def get_app_template(self):
        # Fetch the app template from the  database
        try:
            app_template_id = self.kwargs['template_id']  # Assuming template_id is in the URL
            response = requests.get(f"http://localhost:8000/api/app-templates/{app_template_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            exceptions.handle(self.request, _('Unable to retrieve app template details: %s') % str(e))
            return {}

    def get_image_data(self, image_id):

        # Fetch image details from Glance based on the image_id
        try:
            image = glance.image_get(self.request, image_id)
            return {'visibility': image.visibility, 'owner': image.owner}
        except Exception as e:
            exceptions.handle(self.request, _('Unable to retrieve image details: %s') % str(e))
            return {}


class CreateView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'

    # Add the form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AppTemplateForm()
        return context

class InstancesView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'

    # Add the form to the context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InstanceForm()

        image_id = self.request.GET.get('image_id')
        if image_id:
            context['image_id'] = image_id

        return context
