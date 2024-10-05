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


        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id


        context['username'] = user.username
        context['auth_token'] = token_id

        return context


class DetailPageView(generic.TemplateView):
    template_name = 'identity/eduvmstore/detail.html'



