from django.views import generic
from django.utils.translation import gettext_lazy as _
import sys
from datetime import datetime

from myplugin.content.admin.utils import get_user_details, get_users, get_roles, get_app_templates_to_approve, \
    get_username_from_id, get_app_templates


class IndexView(generic.TemplateView):
    """
        View for displaying the admin index page with user details and admin status.
    """
    template_name = 'eduvmstore_dashboard/admin/index.html'
    page_title = _("EduVMStore Admin")

    def get_context_data(self, **kwargs):
        """
            Add user details, authentication token, and admin status to the context.

            :param kwargs: Additional context parameters.
            :return: Context dictionary with user-specific details and content visibility.
            :rtype: dict
        """
        context = super().get_context_data(**kwargs)
        userdev = self.request.user
        token_id = None

        # Check if the user has a token attribute and retrieve its ID
        if hasattr(self.request, "user") and hasattr(self.request.user, "token"):
            token_id = self.request.user.token.id

        try:
            user_id = self.request.user.id
            user_details = get_user_details(self.request, user_id)
            role_level = user_details.get('role', {}).get('access_level', 1)
        except Exception:
            role_level = 1

        try:
            user_data = get_users(self.request)
        except Exception as e:
            user_data = []

        context['users'] = user_data

        try:
            roles_data = get_roles(self.request)
        except Exception as e:
            roles_data = []
        context['roles'] = roles_data

        admin_access_level = sys.maxsize
        for item in roles_data:
            if item["name"] == "EduVMStoreAdmin":
                admin_access_level = item["access_level"]
                break
        try:
            approvable_app_templates = get_app_templates_to_approve(self.request)
        except Exception as e:
            approvable_app_templates = []
        context['approvable_app_templates'] = approvable_app_templates

        for template in approvable_app_templates:
            creator_id = template.get("creator_id")
            if creator_id:
                app_template_creator_id = creator_id.replace('-', '')
                try:
                    creator_name = get_username_from_id(self.request, app_template_creator_id)
                except Exception as e:
                    creator_name = "unknown"

                template["creator_name"] = creator_name

        try:
            app_templates = get_app_templates(self.request)
        except Exception as e:
            app_templates = []
        context['app_templates'] = app_templates

        try:
            detailed_users = []
            for user in user_data:
                user_id = user.get('id')
                if user_id:
                    user_details = get_user_details(self.request, user_id)
                    user_details_id = user_id.replace('-', '')
                    user_details['username'] = get_username_from_id(self.request, user_details_id)
                    detailed_users.append(user_details)
                updated_at_raw = user_details.get('updated_at')
                if updated_at_raw:
                    dt = datetime.strptime(updated_at_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
                    user_details['updated_at'] = dt.strftime("%d.%m.%Y %H:%M")
        except Exception as e:
            detailed_users = []

        context['detailed_users'] = detailed_users

        # Add user details and admin status to the context
        context['username'] = userdev.username
        context['auth_token'] = token_id
        context['admin'] = userdev.is_superuser
        context['show_content'] = False

        # Check if the user is an admin
        if role_level >= admin_access_level:
            context['show_content'] = True
        else:
            context['show_content'] = False

        context['page_title'] = self.page_title

        return context
