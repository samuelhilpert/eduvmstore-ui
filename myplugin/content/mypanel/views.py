from django.views import generic


class IndexView(generic.TemplateView):
    template_name = 'identity/mypanel/index.html'

def index(request):
    context = {'custom_text': "Dieser Text ist größer und definiert!"}
    return render(request, 'mypanel/index.html', context)
