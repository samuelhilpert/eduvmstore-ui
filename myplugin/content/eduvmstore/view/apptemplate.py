from django.views import generic
from django.shortcuts import render, redirect
from myplugin.content.eduvmstore.utils import get_images_data, get_token_id, get_app_template, get_image_data
import requests
import logging
from django.utils.translation import gettext_lazy as _
from myplugin.content.api_endpoints import API_ENDPOINTS
from django.contrib import messages
from django.urls import reverse
from myplugin.content.eduvmstore.presets import preset_examples
from openstack_dashboard.api import neutron


class AppTemplateView(generic.TemplateView):
    """
    View for creating a new AppTemplate.

    This view handles the display and submission of the form for creating a new AppTemplate.
    It processes the form data, validates it, and sends it to the backend API for creation.
    """

    template_name = 'eduvmstore_dashboard/eduvmstore/create.html'
    page_title = _("Create AppTemplate")

    def dispatch(self, request, *args, **kwargs):
        self.url_mode = request.resolver_match.url_name
        if self.url_mode == "edit":
            self.mode = "edit"
            self.page_title = _("Edit AppTemplate")
        else:
            self.mode = "create"
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to render the create AppTemplate form.

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
        Handle POST requests to create a new AppTemplate.

        This method processes the form data submitted via POST request, validates it,
        and sends it to the backend API for creating a new AppTemplate. It handles
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

        ssh_user_requested = request.POST.get(f'ssh_user_requested', None)

        if ssh_user_requested is None:
            ssh_user_requested = False
        else:
            ssh_user_requested = True

        volume_size = request.POST.get('volume_size', '').strip()
        volume_size_gb = float(volume_size) if volume_size else 0.0

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
            'ssh_user_requested': ssh_user_requested,
            'instantiation_attributes': instantiation_attributes,
            'account_attributes': account_attributes,
            'version': request.POST.get('version'),
            'volume_size_gb': volume_size_gb,
            'fixed_ram_gb': request.POST.get('fixed_ram_gb'),
            'fixed_disk_gb': request.POST.get('fixed_disk_gb'),
            'fixed_cores': request.POST.get('fixed_cores'),
            'security_groups': security_groups
        }

        try:
            if self.mode == "edit":
                template_id = self.kwargs.get("template_id")
                response = requests.put(
                    API_ENDPOINTS['app_template_detail'].format(template_id=template_id),
                    json=data,
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    messages.success(request, "AppTemplate updated successfully.")
                else:
                    messages.error(request, f"Failed to update App-Template. {response.text}")
            else:
                response = requests.post(
                    API_ENDPOINTS['app_templates'],
                    json=data,
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 201:
                    messages.success(request, "AppTemplate created successfully.")
                else:
                    messages.error(request, f"Failed to create App-Template. {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            messages.error(request, f"Failed to create App-Template. Please try again.")

        return redirect(reverse('horizon:eduvmstore_dashboard:eduvmstore:index'))

    def get_context_data(self, **kwargs):
        """
        Add AppTemplate and image data to the context for rendering the template.

        This method fetches the AppTemplate and associated image data if a template ID is provided.
        It also retrieves a list of available images from Glance and adds this information to the context.

        :param kwargs: Additional context parameters.
        :return: Context dictionary with AppTemplate, image visibility, image owner, and available images.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)

        template_id = self.kwargs.get('template_id')
        template_name = self.request.GET.get("template")

        if template_id:
            app_template = get_app_template(self.request, template_id)
            image_data = get_image_data(self.request, app_template.get('image_id', ''))
            db_security_groups = [sg['name'] for sg in app_template.get('security_groups', [])]
        elif template_name in preset_examples and self.mode != "edit":
            app_template = preset_examples[template_name]
            image_data = {}
            db_security_groups = []
        else:
            app_template = {}
            image_data = {}
            db_security_groups = []

        try:
            available_groups = neutron.security_group_list(self.request)
            security_groups = []
            for group in available_groups:
                security_groups.append({
                    'name': group.name,
                    'id': group.id,
                    'selected': group.name in db_security_groups
                })
        except Exception as e:
            logging.error(f"Unable to retrieve security groups: {e}")
            security_groups = []

        context.update({
            'app_template': app_template,
            'image_visibility': image_data.get('visibility', 'N/A'),
            'image_owner': image_data.get('owner', 'N/A'),
            'security_groups': security_groups,
            'is_edit': self.mode == "edit"
        })

        glance_images = get_images_data(self.request)
        context['images'] = [(image.id, image.name) for image in glance_images.values()]
        context['page_title'] = self.page_title

        return context

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
