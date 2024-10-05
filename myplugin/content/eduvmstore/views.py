from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _


class IndexView(generic.TemplateView):
    template_name = 'identity/eduvmstore/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None


        if user.is_authenticated:
            if hasattr(user, "token"):
                token_id = user.token.id

            context['username'] = user.username
            context['auth_token'] = token_id
            context['mail'] = user.email if hasattr(user, 'email') else 'No email available'
        else:
            context['username'] = 'Guest'
            context['auth_token'] = None
            context['mail'] = 'Not available'

        return context


class AccountPageView(generic.TemplateView):
    template_name = 'identity/eduvmstore/account.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None


        if user.is_authenticated:
            if hasattr(user, "token"):
                token_id = user.token.id

            context['username'] = user.username
            context['auth_token'] = token_id
            context['mail'] = user.email if hasattr(user, 'email') else 'No email available'
        else:
             context['username'] = 'Guest'
             context['auth_token'] = None
             context['mail'] = 'Not available'

        return context



