from django.views import generic
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from myplugin.content.eduvmstore.utils import search_app_templates, fetch_favorite_app_templates, \
    get_images_data


class IndexView(generic.TemplateView):
    """
        Display the main index page with available AppTemplates and associated image data.
    """
    template_name = 'eduvmstore_dashboard/eduvmstore/index.html'
    page_title = _("EduVMStore Dashboard")

    def get_context_data(self, **kwargs):
        """
        Add AppTemplates, favorite AppTemplates, and associated image data to the context.

        This method fetches AppTemplates and favorite AppTemplates from the external API,
        retrieves image data from the Glance API, and adds this information to the context
        for rendering the template.

        :param kwargs: Additional context parameters.
        :return: Context dictionary with AppTemplates, favorite AppTemplates, and image details.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)

        try:
            app_templates = search_app_templates(self.request)
        except Exception as e:
            app_templates = []

        try:
            favorite_app_templates = fetch_favorite_app_templates(self.request)
        except Exception as e:
            favorite_app_templates = []

        try:
            glance_images = get_images_data(self.request)
        except Exception as e:
            glance_images = {}

        for app_template in app_templates:
            image_id = app_template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                app_template['size'] = round(glance_image.size / (1024 * 1024), 2)
                app_template['visibility'] = glance_image.visibility
            else:
                app_template['size'] = _('Unknown')
                app_template['visibility'] = _('Unknown')

        for favorite_app_template in favorite_app_templates:
            image_id = favorite_app_template.get('image_id')
            glance_image = glance_images.get(image_id)
            if glance_image:
                favorite_app_template['size'] = round(glance_image.size / (1024 * 1024), 2)
                favorite_app_template['visibility'] = glance_image.visibility
            else:
                favorite_app_template['size'] = _('Unknown')
                favorite_app_template['visibility'] = _('Unknown')

        # Add favorite template IDs to context
        favorite_template_ids = [template['id'] for template in favorite_app_templates]

        context['app_templates'] = app_templates
        context['favorite_app_templates'] = favorite_app_templates
        context['favorite_template_ids'] = favorite_template_ids
        context['page_title'] = self.page_title

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # If the request is AJAX, return only the table partial
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render(request, "eduvmstore_dashboard/eduvmstore/table.html", context)

        return super().get(request, *args, **kwargs)
