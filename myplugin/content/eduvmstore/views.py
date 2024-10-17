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



class IndexView(tabs.TabbedTableView):
    tab_group_class = edu_tabs.MypanelTabs
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        host_ip = get_host_ip()
        context['host_ip'] = host_ip
        return context

    def get_data(self, request, context, *args, **kwargs):
        """Fetch data from Glance and external API, and combine results."""
        # Fetch Glance images
        glance_images = self.get_glance_images(request)

        # Fetch external database data
        external_data = self.get_external_data()

        # Combine the data based on the image ID
        combined_images = self.combine_data(glance_images, external_data)

        context['images'] = combined_images
        return context

    def get_glance_images(self, request):
        """Fetch images from Glance using Horizon API."""
        try:
            filters = {}
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                request, filters=filters, paginate=False
            )
            return images
        except Exception as e:
            logging.error(f"Error fetching images from Glance: {e}")
            return []

    def get_external_data(self):
        """Fetch data from the external API."""
        try:
            response = requests.get("http://localhost:8000/api/app-templates/", timeout=10)
            response.raise_for_status()
            return response.json()  # Assuming this returns a list of templates
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching data from external API: {e}")
            return []

    def combine_data(self, glance_images, external_data):
        """Merge data from Glance and the external API based on image_id."""
        combined_data = []
        external_data_dict = {item['image_id']: item for item in external_data}

        for glance_image in glance_images:
            image_id = glance_image.id
            if image_id in external_data_dict:
                external_info = external_data_dict[image_id]
                combined_data.append({
                    'id': image_id,
                    'name': external_info.get('name', glance_image.name),
                    'short_description': external_info.get('short_description', ''),
                    'version': external_info.get('version', ''),
                    'size': glance_image.size,
                    'owner': glance_image.owner,
                    'visibility': glance_image.visibility,
                })
            else:
                # If there's no matching external data, fall back to Glance data only
                combined_data.append({
                    'id': image_id,
                    'name': glance_image.name,
                    'short_description': '',
                    'version': '',
                    'size': glance_image.size,
                    'owner': glance_image.owner,
                    'visibility': glance_image.visibility,
                })
        return combined_data

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
