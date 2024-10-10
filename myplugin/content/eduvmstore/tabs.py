from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import tabs
import  requests
from openstack_dashboard import api
from openstack_dashboard.api import glance
from scss.extension.compass.helpers import headers
from myplugin.content.eduvmstore import tables

'''
class ImageTab(tabs.TableTab):
    name = _("Images Tab")
    slug = "images_tab"
    table_classes = (tables.ImageTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_images_data(self):
        """Fetch the images from the Glance API and merge with dummy data."""
        try:
            filters = {}  # Add any filters if needed
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            # Fetch the Glance image data using the Horizon API
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # Add dummy data for each image
            images_with_extra_info = []
            for image in images:
                # Get dummy data based on image ID, defaulting to 'N/A' if not found
                extra_info = dummy_data.get(image.id, {
                    'short_description': 'N/A',
                    'description': 'No description available.',
                    'version': 'N/A'
                })
                # Append combined data (Glance + Dummy) to list
                images_with_extra_info.append({
                    'name': image.name,
                    'id': image.id,
                    'status': image.status,
                    'short_description': extra_info['short_description'],
                    'description': extra_info['description'],
                    'version': extra_info['version']
                })

            # Set pagination details
            self._has_more = has_more_data
            return images_with_extra_info

        except Exception as e:
            self._has_more = False
            error_message = _('Unable to retrieve images: %s') % str(e)
            exceptions.handle(self.request, error_message)
            return []

'''
# New Tab for displaying images
class ImageTab(tabs.TableTab):
    name = _("Images Tab")
    slug = "images_tab"
    table_classes = (tables.ImageTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = False

    def has_more_data(self, table):
        return self._has_more

    def get_images_data(self):
        """Fetch the images from the Glance API using the Horizon API."""
        try:
            filters = {}  # Add any filters if needed
            marker = self.request.GET.get(tables.ImageTable._meta.pagination_param, None)

            # Use glance.image_list_detailed from Horizon API
            images, has_more_data, has_prev_data = glance.image_list_detailed(
                self.request, filters=filters, marker=marker, paginate=True
            )

            # Return images and pagination details
            self._has_more = has_more_data
            return images

        except Exception as e:
            self._has_more = False
            error_message = _('Unable to retrieve images: %s') % str(e)
            exceptions.handle(self.request, error_message)
            return []
            


# Tab group that includes both Instances and Images
class MypanelTabs(tabs.TabGroup):
    slug = "mypanel_tabs"
    tabs = (ImageTab, )  # Added the new ImageTab here
    sticky = True


