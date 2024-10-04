from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.template import loader


class IndexView(generic.TemplateView):
    template_name = 'identity/mysecondpanel/index.html'




def testing(request):
    template = loader.get_template('mysecondpanel/index.html')
    context = {
        'firstname': 'Linus',
    }
    return HttpResponse(template.render(context, request))
