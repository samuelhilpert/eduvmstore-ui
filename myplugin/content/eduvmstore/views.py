import requests
from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.conf import settings



class IndexView(generic.TemplateView):
    template_name = 'identity/eduvmstore/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        # OpenStack API call to get user data
        keystone_url = f"http://192.168.64.16/identity/v3/users/{user.id}"
        headers = {
            "X-Auth-Token": token_id,
        }

        try:
            response = requests.get(keystone_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()['user']

            # Add user data to context
            context['username'] = user_data.get('name')
            context['mail'] = user_data.get('email')
        except requests.exceptions.RequestException as e:
            context['error'] = _("Could not retrieve user information: %s") % str(e)

        # Retrieve projects for the current user
        projects_url = f"http://192.168.64.16/identity/v3/projects"
        params = {
            'user_id': user.id,
        }

        try:
            response = requests.get(projects_url, headers=headers, params=params)
            response.raise_for_status()
            projects = response.json()['projects']
            context['projects'] = projects
        except requests.exceptions.RequestException as e:
            context['error_projects'] = _("Could not retrieve projects: %s") % str(e)

        return context


class AccountPageView(generic.TemplateView):
    template_name = 'identity/eduvmstore/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        # OpenStack API call to get user data
        keystone_url = f"http://192.168.64.16/identity/v3/users/{user.id}"
        headers = {
            "X-Auth-Token": token_id,
        }

        try:
            response = requests.get(keystone_url, headers=headers)
            response.raise_for_status()
            user_data = response.json()['user']

            # Add user data to context
            context['username'] = user_data.get('name')
            context['mail'] = user_data.get('email')
        except requests.exceptions.RequestException as e:
            context['error'] = _("Could not retrieve user information: %s") % str(e)

        # Retrieve projects for the current user
        projects_url = f"http://192.168.64.16/identity/v3/projects"
        params = {
            'user_id': user.id,
        }

        try:
            response = requests.get(projects_url, headers=headers, params=params)
            response.raise_for_status()
            projects = response.json()['projects']
            context['projects'] = projects
        except requests.exceptions.RequestException as e:
            context['error_projects'] = _("Could not retrieve projects: %s") % str(e)

        return context



