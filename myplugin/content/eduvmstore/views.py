

import requests
from horizon import tabs

from django.views import generic
from myplugin.content.eduvmstore import tabs as edu_tabs

from django.utils.translation import gettext_lazy as _



class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id


        keystone_url = f"http://10.0.2.15/identity/v3/users/{user.id}"
        headers = {
            "X-Auth-Token": token_id,
        }

        try:
            response = requests.get(keystone_url, headers=headers, timeout=10)
            response.raise_for_status()
            user_data = response.json()['user']


            context['username'] = user_data.get('name')
            context['mail'] = user_data.get('email')
        except requests.exceptions.RequestException as e:
            context['error'] = _("Could not retrieve user information: %s") % str(e)


        if token_id:

            keystone_url = "http://10.0.2.15/identity/v3/auth/projects"
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

class AccountPageView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id


        keystone_url = f"http://10.0.2.15/identity/v3/users/{user.id}"
        headers = {
            "X-Auth-Token": token_id,
        }

        try:
            response = requests.get(keystone_url, headers=headers, timeout=10)
            response.raise_for_status()
            user_data = response.json()['user']


            context['username'] = user_data.get('name')
            context['mail'] = user_data.get('email')
        except requests.exceptions.RequestException as e:
            context['error'] = _("Could not retrieve user information: %s") % str(e)


        if token_id:

            keystone_url = "http://10.0.2.15/identity/v3/auth/projects"
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


class TableView(tabs.TabbedTableView):
    tab_group_class = edu_tabs.MypanelTabs
    template_name = 'eduvmstore_dashboard/eduvmstore/overview.html'

    def get_data(self, request, context, *args, **kwargs):
            user = self.request.user
            token_id = None

            if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
                token_id = self.request.user.token.id

            if token_id:
                glance_url = "http://10.0.2.15/image/v2/images"
                headers = {
                    'X-Auth-Token': token_id,
                    'Content-Type': 'application/json'
                }

                try:
                    response = requests.get(glance_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    images = response.json().get('images', [])
                    context['images'] = images if images else []
                except requests.exceptions.RequestException as e:
                     context['error'] = _("Could not retrieve images: %s") % str(e)

            return context