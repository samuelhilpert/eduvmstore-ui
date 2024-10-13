import requests

import socket
import logging
from horizon import tabs

from openstack_dashboard.api import glance
from django.views import generic
from myplugin.content.eduvmstore import tabs as edu_tabs

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


def get_images_via_rest(request):
    headers = {"X-Auth-Token": request.user.token.id}

    try:
        # Glance API aufrufen, um Images zu holen
        response = requests.get(f"http://{get_host_ip()}/image/v2/images", headers=headers, timeout=10)
        response.raise_for_status()  # Raise error if request fails
        return response.json().get("images", [])  # Return list of images or an empty list
    except requests.exceptions.HTTPError as err:
        print(f"Error fetching images: {err}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error contacting the Glance API: {e}")
        return []


class DetailsPageView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        # Authentifizierungs-Token holen
        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        # Images von der Glance API abrufen
        images = get_images_via_rest(self.request)

        # Bilder und Benutzerinformationen im Kontext speichern
        context['images'] = images
        context['username'] = user.username
        context['auth_token'] = token_id
        context['admin'] = user.is_superuser
        context['show_content'] = user.is_superuser

        return context


'''
class TableView(tabs.TabbedTableView):
    tab_group_class = edu_tabs.MypanelTabs
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_data(self, request, context, *args, **kwargs):

            return context

'''
