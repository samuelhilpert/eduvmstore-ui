import requests

import socket
import logging
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

def get_app_templates(request):
    """Fetch the app templates from the external API."""
    try:
        response = requests.get('http://localhost:8000/api/app-templates/', timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching App Templates: {e}")
        return []


def get_glance_images(request, image_ids):
    """Fetch specific images from Glance based on the list of image IDs."""
    try:
        filters = {'id': image_ids}
        images, _, _ = glance.image_list_detailed(request, filters=filters, paginate=False)
        return {image.id: image for image in images}
    except Exception as e:
        logging.error(f"Error fetching Glance Images: {e}")
        return {}

class IndexView(generic.TemplateView):

    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_data(self, request, context, *args, **kwargs):
        # Fetch App Templates from the external API
        app_templates = get_app_templates(request)

        # Extract all image IDs from the App Templates
        image_ids = [template['image_id'] for template in app_templates]

        # Fetch corresponding Glance Images
        glance_images = get_glance_images(request, image_ids)

        # Combine data from both sources
        combined_data = []
        for template in app_templates:
            image_id = template['image_id']
            glance_image = glance_images.get(image_id)
            if glance_image:
                combined_data.append({
                    'name': template['name'],
                    'short_description': template['short_description'],
                    'version': template['version'],
                    'size': glance_image.size,
                    'visibility': glance_image.visibility,
                })

        context['combined_data'] = combined_data
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
'''
class TableView(tabs.TabbedTableView):
    tab_group_class = edu_tabs.MypanelTabs
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_data(self, request, context, *args, **kwargs):

            return context

'''
