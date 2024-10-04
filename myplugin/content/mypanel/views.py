from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _


class IndexView(generic.TemplateView):
    template_name = 'identity/mypanel/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel_title'] = _("My Panel")  # Setze den Titel für das Panel
        return context

class SecondPageView(generic.TemplateView):
    template_name = 'identity/mypanel/second_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel_title'] = _("Second Page")  # Setze den Titel für die zweite Seite
        return context


def testing(request):
    template = loader.get_template('mypanel/index.html')
    context = {
        'firstname': 'Linus',
    }
    return HttpResponse(template.render(context, request))
