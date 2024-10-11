import requests

import socket
import logging
from horizon import tabs


from django.views import generic
from myplugin.content.eduvmstore import tabs as edu_tabs

from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id



        keystone_url = f"http://{get_host_ip()}/identity/v3/users/{user.id}"


        headers = {
            "X-Auth-Token": token_id,
        }

        try:
            response = requests.get(keystone_url, headers=headers, timeout=10)
            response.raise_for_status()
            user_data = response.json()['user']

            context['auth_token'] = token_id
            context['username'] = user_data.get('name')
            context['mail'] = user_data.get('email')
        except requests.exceptions.RequestException as e:
            context['error'] = _("Could not retrieve user information: %s") % str(e)


        if token_id:


            keystone_url = f"http://{get_host_ip()}/identity/v3/auth/projects"

            

            headers = {'X-Auth-Token': token_id}

            try:
                response = requests.get(keystone_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    projects = response.json().get('projects', [])
                    context['projects'] = projects if projects else None
                else:
                    context['error'] = f"Could not retrieve projects: {response.status_code} {response.text}"

            except requests.RequestException as e:
                context['error'] = f"Error contacting Keystone: {e}"

        return context



    def get_data(self, request, context, *args, **kwargs):

        return context


logger = logging.getLogger(__name__)

class DetailsPageView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image_id = self.kwargs.get('image_id')  # Retrieve image_id from the URL

        try:
            # Assuming token exists and is valid
            token_id = self.request.user.token.id if hasattr(self.request, "user") and hasattr(self.request.user, "token") else None
            if token_id:
                image_url = f"http://{get_host_ip()}/v2/images/{image_id}"
                headers = {"X-Auth-Token": token_id}

                # Make request to OpenStack API
                response = requests.get(image_url, headers=headers, timeout=10)
                response.raise_for_status()  # Raise error for bad responses

                # Log response for debugging
                logger.info(f"OpenStack API response for image {image_id}: {response.json()}")

                # Assign response to context
                context['image'] = response.json()
            else:
                context['error'] = "Authentication token is missing."

        except requests.exceptions.RequestException as e:
            # Log the exact error and pass it to the context for debugging
            logger.error(f"Error fetching image data from OpenStack API: {e}")
            context['error'] = f"Error fetching image data: {e}"

        except Exception as ex:
            # Catch any other general errors
            logger.error(f"Unexpected error: {ex}")
            context['error'] = f"Unexpected error occurred: {ex}"

        return context


'''
class TableView(tabs.TabbedTableView):
    tab_group_class = edu_tabs.MypanelTabs
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_data(self, request, context, *args, **kwargs):

            return context

'''
