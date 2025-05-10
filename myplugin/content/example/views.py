from django.views import generic
from django.utils.translation import gettext_lazy as _
from myplugin.content.eduvmstore.presets import preset_examples

class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/example/index.html'
    page_title = _("Example")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title

        # Add object to the context
        context["preset_examples"] = preset_examples

        # Add simple preset for the test.html fragment
        context["object"] = {"name": "Bob"}

        return context