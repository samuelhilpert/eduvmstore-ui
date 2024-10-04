from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _


class IndexView(generic.TemplateView):
    template_name = 'identity/mypanel/index.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        token_id = None

        # Prüfe, ob der Benutzer authentifiziert ist und ein Token vorhanden ist
        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        # Benutzerinformationen hinzufügen
        context['username'] = user.username
        context['auth_token'] = token_id  # Authentifizierungstoken hinzufügen

        return context


class SecondPageView(generic.TemplateView):
    template_name = 'identity/mypanel/second_page.html'



def testing(request):
    template = loader.get_template('mypanel/index.html')
    context = {
        'firstname': 'Linus',
    }
    return HttpResponse(template.render(context, request))
