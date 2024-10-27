
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
    headers = {"X-Auth-Token": token_id}
    try:
        response = requests.get("http://localhost:8000/api/app-templates/", headers=headers, timeout=10)
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
                template['size'] = round(glance_image.size / (1024 * 1024), 2)
                template['visibility'] = glance_image.visibility
            else:
                template['size'] = _('Unknown')
                template['visibility'] = _('Unknown')

        context['app_templates'] = app_templates
        return context

def get_image_details_via_rest(token_id, image_id):
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
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'
    page_title = "{{ app_template.name }}"

    def get_context_data(self, **kwargs):
        context = super(DetailsPageView, self).get_context_data(**kwargs)
        app_template = self.get_app_template()
        image_data = self.get_image_data(app_template['image_id'])

        context['app_template'] = app_template
        context['image_visibility'] = image_data.get('visibility', 'N/A')
        context['image_owner'] = image_data.get('owner', 'N/A')
        return context

    def get_app_template(self,token_id):
        headers = {"X-Auth-Token": token_id}

        """Fetch the app template from the external database."""
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
        """Fetch image details from Glance based on the image_id."""
        try:
            image = glance.image_get(self.request, image_id)
            return {'visibility': image.visibility, 'owner': image.owner}
        except Exception as e:
            exceptions.handle(self.request, _('Unable to retrieve image details: %s') % str(e))
            return {}


class CreateView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'
    success_url = reverse_lazy('')  # Redirect after successful creation

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request,token_id, *args, **kwargs):
        headers = {"X-Auth-Token": token_id}

        # Retrieve data from the request
        image_id = request.POST.get('image_id')
        name = request.POST.get('name')
        short_description = request.POST.get('short_description')
        description = request.POST.get('description')
        instantiation_notice = request.POST.get('instantiation_notice')
        public = request.POST.get('public')
        version = request.POST.get('version')
        fixed_ram_gb = request.POST.get('fixed_ram_gb')
        fixed_disk_gb = request.POST.get('fixed_disk_gb')
        fixed_cores = request.POST.get('fixed_cores')
        per_user_ram_gb = request.POST.get('per_user_ram_gb')
        per_user_disk_gb = request.POST.get('per_user_disk_gb')
        per_user_cores = request.POST.get('per_user_cores')

        # Prepare the data to be sent to the API
        data = {
            'creator_id': "d110ce1c-800a-484e-b973-4da16d62dcca", # Example creator ID
            'image_id': image_id,
            'name': name,
            'description': description,
            'short_description': short_description,
            'instantiation_notice': instantiation_notice,
            'public': public,
            'version' : version,
            'approved': False,
            'fixed_ram_gb': fixed_ram_gb,
            'fixed_disk_gb': fixed_disk_gb,
            'fixed_cores': fixed_cores,
            'per_user_ram_gb': per_user_ram_gb,
            'per_user_disk_gb': per_user_disk_gb,
            'per_user_cores': per_user_cores,
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
        context = {}
        # Fetch the available images
        glance_images = self.get_images_data()

        # Populate the image choices
        context['images'] = [(image.id, image.name) for image in glance_images]
        return context

    def get_images_data(self):
        """Fetch the images from the Glance API using the Horizon API."""
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
    template_name = 'eduvmstore_dashboard/eduvmstore/instances.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = InstanceForm()

        image_id = self.request.GET.get('image_id')
        if image_id:
            context['image_id'] = image_id

        return context
