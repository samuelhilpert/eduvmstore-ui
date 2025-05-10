from django.views import generic
from myplugin.content.eduvmstore.utils import get_app_template, get_image_data
from openstack_dashboard.api import keystone


class DetailsPageView(generic.TemplateView):
    """
    Display detailed information for a specific AppTemplate, including associated image data.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/details.html'

    def get_context_data(self, **kwargs):
        """
        Add AppTemplate and image data to the context.
        :return: Context dictionary with AppTemplate and image details.
        """
        context = super().get_context_data(**kwargs)
        try:
            app_template = get_app_template(self.request, self.kwargs['template_id'])
        except Exception as e:
            app_template = {}

        try:
            image_data = get_image_data(self.request, app_template.get('image_id', ''))
        except Exception as e:
            image_data = {}

        created_at = app_template.get('created_at', '').split('T')[0]

        creator_id = app_template.get('creator_id', '')
        app_template_creator_id = creator_id.replace('-', '')

        app_template_creator_name = (
            self.get_username_from_id(app_template_creator_id)
            if app_template_creator_id else 'N/A'
        )

        context.update({
            'app_template': app_template,
            'image_visibility': image_data.get('visibility', 'N/A'),
            'image_owner': image_data.get('owner', 'N/A'),
            'app_template_creator': app_template_creator_name,
            'created_at': created_at,
        })

        page_title = app_template.get('name', 'Details')
        context['page_title'] = page_title

        return context

    def get_username_from_id(self, user_id):
        try:
            user = keystone.user_get(self.request, user_id)
            return user.name
        except Exception:
            return user_id
