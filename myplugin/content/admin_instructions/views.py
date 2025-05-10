from django.views import generic
from django.utils.translation import gettext_lazy as _
from myplugin.content.admin_instructions.utils import get_user_details, get_roles
import sys


class IndexView(generic.TemplateView):
    """
        View for displaying the tutorial index page and handling data retrieval from a backend API.
    """
    template_name = 'eduvmstore_dashboard/admin_instructions/index.html'
    page_title = _("Admin Instructions")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        userdev = self.request.user
        user_id = userdev.id

        user_details = get_user_details(self.request, user_id)
        role_level = user_details.get('role', {}).get('access_level', 1)

        roles_data = get_roles(self.request)
        admin_access_level = sys.maxsize
        for item in roles_data:
            if item["name"] == "EduVMStoreAdmin":
                admin_access_level = item["access_level"]
                break

        context['show_content'] = False

        # Check if the user is an admin
        if role_level >= admin_access_level:
            context['show_content'] = True
        else:
            context['show_content'] = False

        context['username'] = userdev.username
        context['page_title'] = self.page_title
        return context
