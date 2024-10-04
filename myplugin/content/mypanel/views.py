from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader
from horizon import views


class IndexView(generic.TemplateView):
    template_name = 'identity/mypanel/index.html'

class SecondPageView(views.HorizonTemplateView):
    template_name = 'mypanel/second_page.html'
    page_title = _("Second Page")


def testing(request):
    template = loader.get_template('mypanel/index.html')
    context = {
        'firstname': 'Linus',
    }
    return HttpResponse(template.render(context, request))
