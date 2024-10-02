from django.shortcuts import render
from django.views import generic
from django.http import HttpResponse
from django.template import loader


class IndexView(generic.TemplateView):
    template_name = 'identity/mypanel/index.html'

def testing(request):
    template = loader.get_template('index.html')
    context = {
        'firstname': 'Linus',
    }
    return HttpResponse(template.render(context, request))

def second_page(request):
    return render(request, 'mypanel/second_page.html')
