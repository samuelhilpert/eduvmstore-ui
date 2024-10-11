from asyncio import timeout

from django.views import generic
from horizon import exceptions
from openstack_dashboard.api import glance
import requests
from django.utils.translation import gettext_lazy as _


class IndexView(generic.TemplateView):
    template_name = 'eduvmstore_dashboard/tutorial/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        context['username'] = user.username
        context['auth_token'] = token_id
        context['admin'] = user.is_superuser
        context['show_content'] = user.is_superuser

        # Funktion zur API-Abfrage von Benutzer- oder Projektnamen


        return context
