from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.utils.translation import gettext_lazy as _

import requests
from django.views.decorators.csrf import csrf_exempt

#THIS CODE IS NOT USED AT THE MOMENT

class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/example/index.html'
    page_title = _("Example")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context